import random

# Bodovna vrijednost figura za procjenu pozicije; pozitivne za bijele, negativne za crne
pieceScore = {
    'white pawn': 1,
    'white knight': 3,
    'white bishop': 3,
    'white rook': 5,
    'white queen': 9,
    'white king': 0,
    'black pawn': -1,
    'black knight': -3,
    'black bishop': -3,
    'black rook': -5,
    'black queen': -9,
    'black king': 0
}

CHECKMATE = 1000  # Velika vrijednost za šah-mat poziciju
STALEMATE = 0     # Nema pobjednika, remi
MAX_DEPTH = 3     # Maksimalna dubina pretrage (može se povećati za jaču, ali sporiju AI)

# Funkcija koja vraća nasumični validni potez (za testiranje ili slabiju AI)
def findRandomMove(validMoves):
    return random.choice(validMoves)

# Pronalazi najbolji potez koristeći minimax algoritam sa dubinom MAX_DEPTH
def findBestMove(gs, validMoves):
    bestMove = None
    bestScore = -CHECKMATE  # Početni najbolji skor što je vrlo nizak

    for move in validMoves:
        gs.makeMove(move)  # Napravi potez na tabli
        # Rekurzivno pozovi minimax za protivnika sa smanjenom dubinom
        score = -minimax(gs, MAX_DEPTH - 1, -1 if gs.whiteToMove else 1)
        gs.undoMove()  # Vraćanje na staru poziciju nakon procjene
        if score > bestScore:
            bestScore = score
            bestMove = move

    return bestMove


# Druga verzija minimaxa, sa globalnom varijablom nextMove za čuvanje poteza
def bestMinMax(gs, validMoves):
    global nextMove
    nextMove = None
    minimax(gs, validMoves, MAX_DEPTH, gs.whiteToMove)
    return nextMove

# Klasični minimax algoritam sa dvije strane (maksimizira i minimizira)
def minimax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)  # Evaluacija materijala na tabli

    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()  # Dobij validne poteze protivnika
            score = minimax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                # Ako smo na vrhu pretrage, zapamti potez
                if depth == MAX_DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            # Greška u tvojoj verziji: koristi MAX_DEPTH umjesto depth-1, treba popraviti
            score = minimax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == MAX_DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore


# -------------

# NegaMax algoritam sa alfa-beta prunerom za efikasnije pretraživanje
def findBestMoveNegaMax(gs, validMoves, depth):
    bestMove = None
    bestScore = -CHECKMATE
    alpha = -CHECKMATE  # Donja granica (najgore što može biti)
    beta = CHECKMATE    # Gornja granica (najbolje što može biti)
    turnMultiplier = 1 if gs.whiteToMove else -1  # Koji je igrač na potezu

    for move in validMoves:
        gs.makeMove(move)
        # Rekurzivno pozivanje negaMax sa obrnutim znakom i ažuriranim alpha/beta
        score = -negaMaxAlphaBeta(gs, depth - 1, -beta, -alpha, -turnMultiplier)
        gs.undoMove()
        if score > bestScore:
            bestScore = score
            bestMove = move
        alpha = max(alpha, score)  # Ažuriraj alpha
    return bestMove


# Glavna funkcija negaMax sa alfa-beta orezivanjem
def negaMaxAlphaBeta(gs, depth, alpha, beta, turnMultiplier):
    if depth == 0:
        # Na dubini 0 procijeni poziciju i vrati rezultat
        return turnMultiplier * scoreBoard(gs)

    validMoves = gs.getValidMoves()
    if not validMoves:
        # Ako nema poteza, procijeni poziciju (mat ili remi)
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        score = -negaMaxAlphaBeta(gs, depth - 1, -beta, -alpha, -turnMultiplier)
        gs.undoMove()

        if score > maxScore:
            maxScore = score
        alpha = max(alpha, score)

        if alpha >= beta:  # Beta cut-off, preskače nepotrebne grane
            break
    return maxScore


# -------------

# Procjena materijala na tabli bez pozicionih faktora
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square != "--":
                score += pieceScore.get(square, 0)
    return score


# Tabele za pozicijsku procjenu za svaku figuru po polju (heurističke vrijednosti)
pawn_table = [
    [0,   0,   0,   0,   0,   0,   0,   0],
    [5,  10,  10, -20, -20, 10, 10,   5],
    [5,  -5, -10,   0,   0,-10, -5,   5],
    [0,   0,   0,  20,  20,  0,  0,   0],
    [5,   5,  10,  25,  25, 10,  5,   5],
    [10, 10,  20,  30,  30, 20, 10,  10],
    [50, 50,  50,  50,  50, 50, 50,  50],
    [0,   0,   0,   0,   0,  0,  0,   0]
]

knight_table = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20,   0,   5,   5,   0, -20, -40],
    [-30,   5,  10,  15,  15, 10,   5, -30],
    [-30,   0,  15,  20,  20, 15,   0, -30],
    [-30,   5,  15,  20,  20, 15,   5, -30],
    [-30,   0,  10,  15,  15, 10,   0, -30],
    [-40, -20,   0,   0,   0,   0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50]
]

bishop_table = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10,   5,   0,   0,   0,   0,   5, -10],
    [-10,  10,  10,  10,  10,  10,  10, -10],
    [-10,   0,  10,  10,  10,  10,   0, -10],
    [-10,   5,   5,  10,  10,   5,   5, -10],
    [-10,   0,   5,  10,  10,   5,   0, -10],
    [-10,   0,   0,   0,   0,   0,   0, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20]
]

rook_table = [
    [0,   0,   5,  10,  10,   5,   0,   0],
    [-5,  0,   0,   0,   0,   0,   0,  -5],
    [-5,  0,   0,   0,   0,   0,   0,  -5],
    [-5,  0,   0,   0,   0,   0,   0,  -5],
    [-5,  0,   0,   0,   0,   0,   0,  -5],
    [-5,  0,   0,   0,   0,   0,   0,  -5],
    [5,  10,  10,  10,  10,  10,  10,   5],
    [0,   0,   0,   0,   0,   0,   0,   0]
]

queen_table = [
    [-20, -10, -10,  -5,  -5, -10, -10, -20],
    [-10,   0,   5,   0,   0,   0,   0, -10],
    [-10,   5,   5,   5,   5,   5,   0, -10],
    [0,     0,   5,   5,   5,   5,   0,  -5],
    [-5,    0,   5,   5,   5,   5,   0,  -5],
    [-10,   0,   5,   5,   5,   5,   0, -10],
    [-10,   0,   0,   0,   0,   0,   0, -10],
    [-20, -10, -10,  -5,  -5, -10, -10, -20]
]

king_table = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20,  20,   0,   0,   0,   0,  20,  20],
    [20,  30,  10,   0,   0,  10,  30,  20]
]

# Funkcija koja računa ukupnu procjenu pozicije sa materijalom i pozicijskim bonusima
def scoreBoard(gs):
    if gs.checkmate:
        # Ako je šah-mat, daj veliku vrijednost u korist pobjednika
        return -CHECKMATE if gs.whiteToMove else CHECKMATE
    elif gs.stalemate:
        # Remi daje neutralnu vrijednost
        return STALEMATE

    score = 0
    board = gs.board
    # Prođi kroz svako polje i zbroji bodove za figuru i poziciju
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece != "--":
                color, piece_type = piece.split()
                table_score = 0
                # Dodaj pozicijske bodove zavisno od boje i tipa figure
                if piece_type == "pawn":
                    table_score = pawn_table[r][c] if color == "white" else -pawn_table[7 - r][c]
                elif piece_type == "knight":
                    table_score = knight_table[r][c] if color == "white" else -knight_table[7 - r][c]
                elif piece_type == "bishop":
                    table_score = bishop_table[r][c] if color == "white" else -bishop_table[7 - r][c]
                elif piece_type == "rook":
                    table_score = rook_table[r][c] if color == "white" else -rook_table[7 - r][c]
                elif piece_type == "queen":
                    table_score = queen_table[r][c] if color == "white" else -queen_table[7 - r][c]
                elif piece_type == "king":
                    table_score = king_table[r][c] if color == "white" else -king_table[7 - r][c]

                material_score = pieceScore.get(piece, 0)
                score += material_score + table_score
    return score
