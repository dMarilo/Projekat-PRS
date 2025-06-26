"""
Ovaj fajl rukuje korisničkim unosom i prikazuje trenutno stanje igre šaha
"""

import pygame as p
import ChessEngine
import chessAI

import tkinter as tk
from tkinter import messagebox
import sys
import os


# Dimenzije prozora i table
WIDTH = HEIGHT = 1024
DIMENSION = 8  # Tabla je 8x8 polja
SQ_SIZE = HEIGHT // DIMENSION  # Veličina jednog polja na tabli
MAX_FPS = 15  # Maksimalni broj frejmova po sekundi (za osvježavanje ekrana)
IMAGES = {}  # Rječnik u kojem ćemo čuvati slike figura


def loadImages():
    """
    Učitava slike svih figura i skalira ih na veličinu polja.
    Slike se nalaze u folderu 'images', a ključevi u rječniku su nazivi figura.
    """
    pieces = ['white rook', 'white knight', 'white bishop', 'white queen', 'white king', 'white pawn',
              'black rook', 'black knight', 'black bishop', 'black queen', 'black king', 'black pawn']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    """
    Glavna funkcija programa.
    Inicijalizuje pygame, kreira ekran i sat za kontrolu FPS,
    učitava slike figura, i u petlji prikazuje stanje igre i obrađuje događaje.
    """
    p.init()  # Inicijalizacija pygame biblioteke
    screen = p.display.set_mode((WIDTH, HEIGHT))  # Kreiranje prozora za igru
    clock = p.time.Clock()  # Sat za kontrolu vremena
    screen.fill(p.Color("white"))  # Postavljanje bijele pozadine na ekran

    gs = ChessEngine.GameState()  # Kreiranje objekta koji drži stanje igre (tablu itd.)
    log_file = open(get_next_log_filename(), "w")

    validMoves = gs.getValidMoves() 
    moveMade = False #Flag variable kad je neki potez povucen
    loadImages()  # Učitavanje i priprema slika figura

    running = True  # Kontrola glavne petlje
    
    sqSelected = () #Nije ni jedno polje oznaceno, ali ce pratiti koje je zadnje polje kliknuto
    playerClicks = [] #Prati klikove
    
    
    playerOne = True #If a human is playing white, this will be true, if ai, then false
    playerTwo = False #Same as above for black
    
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():  # Petlja za hvatanje svih događaja (npr. klikova, zatvaranja prozora)
            if e.type == p.QUIT:  # Ako je korisnik zatvorio prozor
                running = False  # Prekini glavnu petlju i izađi iz programa
            
            #mouse handler
                
            elif e.type == p.MOUSEBUTTONDOWN:
                if humanTurn:
                    # Dobijanje pozicije miša kada korisnik klikne
                    location = p.mouse.get_pos()  # (x, y) koordinate kliknutog mjesta
                    
                    # Izračunavanje kolone i reda na osnovu kliknute pozicije
                    col = location[0] // SQ_SIZE  # kolona (0–7)
                    row = location[1] // SQ_SIZE  # red (0–7)

                    # Ako je korisnik dva puta kliknuo isto polje, resetuj izbor
                    if sqSelected == (row, col):
                        sqSelected = ()          # poništi trenutno označeno polje
                        playerClicks = []        # poništi listu klikova
                    else:
                        # Inače, zapamti novo polje koje je kliknuto
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # dodaj u listu klikova

                    # Ako su dva klika zabilježena (odabrana figura i cilj)
                    if len(playerClicks) == 2:
                        # Kreiraj objekt poteza koristeći početnu i krajnju poziciju
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)

                        # Dohvati figuru koja se pokušava pomjeriti
                        piece = gs.board[move.startRow][move.startCol]

                        # Provjeri da li figura pripada igraču koji je na potezu
                        if (gs.whiteToMove and piece.startswith('white')) or (not gs.whiteToMove and piece.startswith('black')):
                            print(move.getChessNotation())  # ispiši potez u šahovskoj notaciji u konzolu
                            log_file.write(move.getChessNotation() + "\n")
                            
                            if move in validMoves:
                                gs.makeMove(move)  # izvrši potez
                                moveMade = True 

                            # Resetuj izbor nakon pokušaja poteza (bilo da je važeći ili ne)
                                sqSelected = ()
                                playerClicks = []
                            else:
                                playerClicks = [sqSelected]
                        else:
                            # Invalid first piece, reset everything
                            sqSelected = ()
                            playerClicks = []
            
            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True

        from monte_carlo_ai import mcts_best_move



        #AI move finder
        if not humanTurn:
            AIMove = chessAI.findBestMoveNegaMax(gs, validMoves, 6)
            #AIMove = mcts_best_move(gs, iterations=100)

            #AIMove = chessAI.findBestMove(gs, validMoves)
            if AIMove is None:
                print("Random")
                AIMove = chessAI.findRandomMove(validMoves)
            gs.makeMove(AIMove)

            moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()

            moveMade = False    

        drawGameState(screen, gs, sqSelected)  # Iscrtavanje trenutnog stanja igre (tabla + figure)
        
        
        if gs.checkmate:
            winner = "Black" if gs.whiteToMove else "White"
            loser = "White" if gs.whiteToMove else "Black"
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("Game Over", f"{winner} has won the game by checkmate.\n{loser} has lost.")
            log_file.close()

            p.quit()
        

        clock.tick(MAX_FPS)  # Ograničava broj frejmova u sekundi na MAX_FPS
        p.display.flip()  # Ažurira ekran da se prikažu sve promjene


def drawGameState(screen, gs, sqSelected):
    """
    Iscrtava cijelu igru:
    - tablu
    - figure
    """
    drawBoard(screen)  # Iscrtavanje table
    highlightSquare(screen, gs, sqSelected)
    drawPieces(screen, gs.board)  # Iscrtavanje figura na osnovu trenutnog stanja table
    highlightKing(screen, gs)
    
# Funkcija za označavanje trenutno selektovanog polja na tabli
def highlightSquare(screen, gs, sqSelected):
    if sqSelected != ():  # Ako je neko polje selektovano
        r, c = sqSelected
        # Provjeri da li se na tom polju nalazi figura trenutnog igrača
        if gs.board[r][c] != '--' and (
            (gs.whiteToMove and gs.board[r][c].startswith('white')) or
            (not gs.whiteToMove and gs.board[r][c].startswith('black'))
        ):
            # Kreiraj providni kvadrat za označavanje
            s = p.Surface((SQ_SIZE, SQ_SIZE))  # Površina iste veličine kao jedno polje
            s.set_alpha(100)  # Postavi providnost (0 = potpuno providno, 255 = neprovidno)
            s.fill(p.Color('blue'))  # Postavi boju kvadrata
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))  # Prikaži kvadrat na pravoj poziciji
            
            
# Funkcija za označavanje kralja ako je u šahu ili matiran
def highlightKing(screen, gs):
    # Odredi poziciju kralja na osnovu boje igrača koji je trenutno na potezu
    king_pos = gs.whiteKingLocation if gs.whiteToMove else gs.blackKingLocation

    # Odredi boju označavanja:
    if gs.checkmate:
        color = p.Color("darkred")  # Crvena boja za šah-mat
    elif gs.inCheck:
        color = p.Color("yellow")   # Žuta boja za šah
    else:
        return  # Ako nije ni šah ni mat, ne označava se ništa

    # Kreiraj providni kvadrat za označavanje kralja
    s = p.Surface((SQ_SIZE, SQ_SIZE))  # Površina iste veličine kao jedno polje
    s.set_alpha(100)  # Providnost
    s.fill(color)  # Boja prema stanju (šah/šah-mat)
    screen.blit(s, (king_pos[1] * SQ_SIZE, king_pos[0] * SQ_SIZE))  # Prikaži kvadrat na poziciji kralja





def drawBoard(screen):
    """
    Iscrtava šahovsku tablu sa naizmjeničnim bojama polja (bijelo i sivo).
    """
    colors = [p.Color("white"), p.Color("brown")]  # Boje za polja table
    for r in range(DIMENSION):  # Redovi (0-7)
        for c in range(DIMENSION):  # Kolone (0-7)
            color = colors[(r + c) % 2]  # Naizmjenična boja polja (kao kod šaha)
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))  # Iscrtavanje polja


def drawPieces(screen, board):
    """
    Iscrtava figure na tabli.
    Prolazi kroz svako polje na tabli i ako nije prazno ('--'),
    iscrtava odgovarajuću sliku figure.
    """
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # Ako ima figura na ovom polju
                # Iscrtaj sliku figure na odgovarajuću poziciju na ekranu
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def get_next_log_filename(log_dir="log", base_name="game", extension=".txt"):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    existing_files = os.listdir(log_dir)
    index = 1
    while f"{base_name}{index}{extension}" in existing_files:
        index += 1

    return os.path.join(log_dir, f"{base_name}{index}{extension}")


# Kada se ovaj fajl direktno pokrene, poziva se main funkcija
if __name__ == "__main__":
    main()
