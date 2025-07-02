import random
import pygame as p
import tkinter as tk
from tkinter import messagebox
import os
from concurrent.futures import ThreadPoolExecutor

import ChessEngine
from OpeningBook import OPENINGS
from monte_carlo_ai import parallel_mcts

# Constants
WIDTH = HEIGHT = 720
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}

executor = ThreadPoolExecutor(max_workers=1)

def loadImages():
    pieces = [
        'white rook', 'white knight', 'white bishop', 'white queen', 'white king', 'white pawn',
        'black rook', 'black knight', 'black bishop', 'black queen', 'black king', 'black pawn'
    ]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE)
        )

def get_next_log_filename(log_dir="log", base_name="game", extension=".txt"):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    index = 1
    while f"{base_name}{index}{extension}" in os.listdir(log_dir):
        index += 1
    return os.path.join(log_dir, f"{base_name}{index}{extension}")

def drawBoard(screen):
    colors = [p.Color("white"), p.Color("brown")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlightSquare(screen, gs, sqSelected):
    if sqSelected:
        r, c = sqSelected
        if gs.board[r][c] != '--' and ((gs.whiteToMove and gs.board[r][c].startswith('white')) or
                                       (not gs.whiteToMove and gs.board[r][c].startswith('black'))):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

def highlightKing(screen, gs):
    king_pos = gs.whiteKingLocation if gs.whiteToMove else gs.blackKingLocation
    if gs.checkmate:
        color = p.Color("darkred")
    elif gs.inCheck:
        color = p.Color("yellow")
    else:
        return
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(100)
    s.fill(color)
    screen.blit(s, (king_pos[1] * SQ_SIZE, king_pos[0] * SQ_SIZE))

def drawGameState(screen, gs, sqSelected):
    drawBoard(screen)
    highlightSquare(screen, gs, sqSelected)
    drawPieces(screen, gs.board)
    highlightKing(screen, gs)

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = ChessEngine.GameState()
    log_file = open(get_next_log_filename(), "w")

    validMoves = gs.getValidMoves()
    moveMade = False
    sqSelected = ()
    playerClicks = []
    playerOne = True
    playerTwo = False

    aiThinking = False
    aiMove = None
    aiFuture = None

    loadImages()
    running = True

    book_line = None
    book_index = 0
    book_attempted = False

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN and humanTurn:
                loc = p.mouse.get_pos()
                col, row = loc[0] // SQ_SIZE, loc[1] // SQ_SIZE
                if sqSelected == (row, col):
                    sqSelected, playerClicks = (), []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)

                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    piece = gs.board[move.startRow][move.startCol]
                    if (gs.whiteToMove and piece.startswith('white')) or (not gs.whiteToMove and piece.startswith('black')):
                        if move in validMoves:
                            gs.makeMove(move)
                            log_file.write(move.getChessNotation() + "\n")
                            moveMade = True

                            # ✅ Advance book tracking
                            if book_line and book_index < len(book_line):
                                expected = book_line[book_index]
                                if move.getChessNotation() == expected:
                                    book_index += 1
                                else:
                                    print(f"[📘 Opening] User deviated from book line.")
                                    book_line = None

                            sqSelected, playerClicks = (), []

                    else:
                        playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN and e.key == p.K_z:
                gs.undoMove()
                validMoves = gs.getValidMoves()
                moveMade = False
                aiThinking = False
                aiMove = None
                aiFuture = None
                book_line = None
                book_index = 0
                book_attempted = False

        if not book_line and not book_attempted and len(gs.moveLog) == 1:
            first = tuple(m.getChessNotation() for m in gs.moveLog[:1])
            book_options = OPENINGS.get(first)
            if book_options:
                book_line = random.choice(book_options)
                book_index = 0
                print(f"[📘 Opening] Using book line: {' '.join(book_line)}")
            book_attempted = True

        if not humanTurn and not aiThinking:
            if book_line and book_index < len(book_line):
                expected = book_line[book_index]
                for move in validMoves:
                    if move.getChessNotation() == expected:
                        print(f"[📘 Book Move] {expected}")
                        gs.makeMove(move)
                        log_file.write(move.getChessNotation() + "\n")
                        moveMade = True
                        book_index += 1
                        if book_index >= len(book_line):
                            book_line = None
                        break
                else:
                    print("[📘 Book deviation] Falling back to AI.")
                    book_line = None
            else:
                print("Submitting AI move to background thread...")
                aiThinking = True
                aiFuture = executor.submit(parallel_mcts, gs, iterations=300, max_workers=4)

        if aiThinking and aiFuture and aiFuture.done():
            aiMove = aiFuture.result()
            if aiMove:
                print("AI chose:", aiMove.getChessNotation())
                gs.makeMove(aiMove)
                log_file.write(aiMove.getChessNotation() + "\n")
                moveMade = True
            aiThinking = False
            aiFuture = None

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, sqSelected)

        if gs.checkmate:
            winner = "Black" if gs.whiteToMove else "White"
            tk.Tk().withdraw()
            messagebox.showinfo("Game Over", f"{winner} wins by checkmate.")
            log_file.close()
            p.quit()

        clock.tick(MAX_FPS)
        p.display.flip()

if __name__ == "__main__":
    main()