"""
Ova klasa je odgovorna za čuvanje svih informacija o trenutnom stanju šahovske partije.
Također će biti zadužena za određivanje validnih poteza u datom trenutku.
Čuva i evidenciju svih odigranih poteza (move log).
"""

class GameState():
    
    def __init__(self):
        # Inicijalno postavljanje šahovske table kao 8x8 lista lista,
        # gdje svaki element predstavlja figuru ili prazno polje ('--')
        self.board = [
            ["black rook", "black knight", "black bishop", "black queen", "black king", "black bishop", "black knight", "black rook"],
            ["black pawn", "black pawn", "black pawn", "black pawn", "black pawn", "black pawn", "black pawn", "black pawn"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["white pawn", "white pawn", "white pawn", "white pawn", "white pawn", "white pawn", "white pawn", "white pawn"],
            ["white rook", "white knight", "white bishop", "white queen", "white king", "white bishop", "white knight", "white rook"]
        ]
        
        # Mapa funkcija za kreiranje poteza za svaki tip figure
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        # Zastavica koja pokazuje čiji je red za potez (True = bijeli, False = crni)
        self.whiteToMove = True

        # Početne pozicije kraljeva
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        # Informacije o rošadi (prava rošade za obje strane)
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
                                     self.currentCastlingRights.bks, self.currentCastlingRights.bqs)]

        self.inCheck = False  # Zastavica da li je trenutni igrač pod šahom
        self.checkmate = False  # Zastavica da li je igra završena matom
        self.stalemate = False  # Zastavica da li je remi
        self.pins = []  # Liste za pinovane figure
        self.checks = []  # Liste za prijetnje šahom

        # Polje na kojem je trenutno moguć en passant
        self.enPassantPossible = ()

        # Lista u koju će se spremati svi odigrani potezi (za praćenje igre i eventualno vraćanje poteza)
        self.moveLog = []

    def makeMove(self, move):
        # Osiguraj da je argument zaista objekat klase Move
        assert isinstance(move, Move), "Expected a Move object"
        
        # Postavi početno polje na prazno
        self.board[move.startRow][move.startCol] = "--"
        
        # Postavi krajnje polje na figuru koja se pomjera
        self.board[move.endRow][move.endCol] = move.pieceMoved

        # Ako je potez promocija pješaka
        if move.isPawnPromotion:
            promotedColor = "white" if self.whiteToMove else "black"
            self.board[move.endRow][move.endCol] = promotedColor + " " + move.promotionPiece
        else:
            self.board[move.endRow][move.endCol] = move.pieceMoved

        # Dodaj ovaj potez u listu odigranih poteza
        self.moveLog.append(move)

        # Zamijeni red: ako je bio potez bijelog → sad je crni, i obrnuto
        self.whiteToMove = not self.whiteToMove

        # Ažuriraj poziciju kralja ako se on pomjera
        if move.pieceMoved == "white king":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "black king":
            self.blackKingLocation = (move.endRow, move.endCol)

        # En passant potez — uklanja pješaka koji je pojedene en passant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        # Ako je pješak pomjeren za dva polja unaprijed, postavi mogućnost en passant
        if move.pieceMoved.split()[1] == 'pawn' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enPassantPossible = ()

        # Ako je potez rošada
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # kingside rošada
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][7]  # premještanje topa
                self.board[move.endRow][7] = "--"
            else:  # queenside rošada
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][0]
                self.board[move.endRow][0] = "--"

        # Ažuriraj prava na rošadu
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
                                         self.currentCastlingRights.bks, self.currentCastlingRights.bqs))


    def undoMove(self):
        # Vraća zadnji potez ako postoji i poništava ga
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            assert isinstance(move, Move), f"Očekivan Move objekat, dobio: {type(move)}"

            # Vrati figuru na početnu poziciju
            self.board[move.startRow][move.startCol] = move.pieceMoved

            # Vrati figuru koja je bila pojedena (ili "--" ako nije bilo uzimanja)
            self.board[move.endRow][move.endCol] = move.pieceCaptured

            # Promijeni čiji je red na potez
            self.whiteToMove = not self.whiteToMove

            # Vrati kralja na prethodnu poziciju ako se on pomjerao
            if move.pieceMoved == "white king":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "black king":
                self.blackKingLocation = (move.startRow, move.startCol)

            # Ako je potez bio en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"  # ukloni "lažnu" figuru
                self.board[move.startRow][move.endCol] = move.pieceCaptured  # vrati pješaka koji je bio pojeden en passant

            # Poništi zadnja prava na rošadu (vrati na stanje prije tog poteza)
            self.castleRightsLog.pop()
            self.currentCastlingRights = self.castleRightsLog[-1]

            # Ako je potez bio rošada, vrati topa na originalnu poziciju
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # kingside rošada
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:  # queenside rošada
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

    def updateCastleRights(self, move):
        # Ažurira prava na rošadu ako se kralj ili top pomjerio (ili bio pojedene)
        if move.pieceMoved == "white king":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "black king":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "white rook":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wqs = False  # queenside top
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False  # kingside top
        elif move.pieceMoved == "black rook":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False

    # Glavna funkcija koja vraća sve validne poteze (koji ne izlažu kralja šahu)
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()  # Provjera da li je kralj ugrožen

        if self.whiteToMove:
            kingRow, kingCol = self.whiteKingLocation
        else:
            kingRow, kingCol = self.blackKingLocation

        if self.inCheck:
            if len(self.checks) == 1:
                # Samo jedan napadač – moguće blokirati ili uzeti
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow, checkCol = check[0], check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []

                # Ako figura koja napada nije konj, moguće je blokirati liniju napada
                if pieceChecking.split()[1] != "knight":
                    d = (check[2], check[3])  # smjer napada
                    for i in range(1, 8):
                        validSquare = (kingRow + d[0] * i, kingCol + d[1] * i)
                        validSquares.append(validSquare)
                        if validSquare == (checkRow, checkCol):
                            break
                validSquares.append((checkRow, checkCol))  # ili pojesti napadača

                # Zadrži samo poteze koji vode na validna polja
                moves = [m for m in moves if m.pieceMoved.split()[1] == "king" or (m.endRow, m.endCol) in validSquares]
            else:
                # Dvostruki šah – kralj se mora pomjeriti
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()

        #Provjera kraja igre: mat ili remi
        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
            return moves

    # Svi mogući potezi (bez obzira da li su legalni u šahovskom smislu – npr. šah)
    def getAllPossibleMoves(self, includeCastle=True):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]
                if piece == "--":
                    continue
                if (piece.startswith("white") and self.whiteToMove) or \
                (piece.startswith("black") and not self.whiteToMove):

                    pieceType = piece.split()[1]  # "pawn", "rook", itd.

                    # Mapiranje figure u karakter koji se koristi za pristup odgovarajućoj funkciji
                    pieceLetter = {
                        "pawn": "p",
                        "rook": "R",
                        "knight": "N",
                        "bishop": "B",
                        "queen": "Q",
                        "king": "K"
                    }.get(pieceType)

                    if pieceLetter in self.moveFunctions:
                        if pieceLetter == "K":
                            # Proslijedi flag za rošadu samo za kralja
                            self.moveFunctions[pieceLetter](r, c, moves, includeCastle)
                        else:
                            self.moveFunctions[pieceLetter](r, c, moves)
                    else:
                        print(f"Greška: nepoznata figura {pieceType} na {r},{c}")
        return moves


    # Funkcija koja određuje pinove (vezane figure) i prijetnje šahom
    def checkForPinsAndChecks(self):
        pins = []       # lista svih figura koje su "vezane" (ne smiju se pomjeriti jer bi otkrile kralja)
        checks = []     # lista svih prijetnji kralju (šahova)
        inCheck = False # da li je trenutni kralj pod šahom

        # Odredi boje protivnika i saveznika, kao i poziciju trenutnog kralja
        if self.whiteToMove:
            enemyColor = "black"
            allyColor = "white"
            startRow, startCol = self.whiteKingLocation
        else:
            enemyColor = "white"
            allyColor = "black"
            startRow, startCol = self.blackKingLocation

        # 8 pravaca za provjeru (gore, dolje, lijevo, desno, dijagonale)
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1),
                    (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for j, d in enumerate(directions):
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0]*i
                endCol = startCol + d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece.startswith(allyColor) and endPiece.split()[1] != "king":
                        if possiblePin == ():
                            # Moguća figura koja je pinovana
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break  # već imamo jednu savezničku figuru u liniji - nema pina
                    elif endPiece.startswith(enemyColor):
                        type = endPiece.split()[1]
                        # Provjeri da li ta figura može ugroziti kralja iz tog pravca
                        if ((0 <= j <= 3 and type == "rook") or
                            (4 <= j <= 7 and type == "bishop") or
                            (i == 1 and type == "pawn" and
                            ((enemyColor == "white" and 6 <= j <= 7) or
                            (enemyColor == "black" and 4 <= j <= 5))) or
                            (type == "queen") or (i == 1 and type == "king")):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                # figura je pinovana jer iza nje stoji napadač
                                pins.append(possiblePin)
                            break
                        else:
                            break
                else:
                    break

        # Provjera šaha od skakača (konja)
        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                    (1, -2), (1, 2), (2, -1), (2, 1)]
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece.startswith(enemyColor) and endPiece.split()[1] == "knight":
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))

        return inCheck, pins, checks


    # Generiši sve poteze pješaka u zavisnosti od boje, pina i en passant pravila
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        # Provjera da li je figura pinovana (vezana)
        for i in range(len(self.pins)):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                break

        if self.whiteToMove:
            # Jedno polje naprijed
            if self.board[r - 1][c] == "--":
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    # Dva polja naprijed sa početne pozicije
                    if r == 6 and self.board[r - 2][c] == "--":
                        moves.append(Move((r, c), (r - 2, c), self.board))

            # Jedenje lijevo
            if c - 1 >= 0:
                if self.board[r - 1][c - 1].startswith("black"):
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))

            # Jedenje desno
            if c + 1 <= 7:
                if self.board[r - 1][c + 1].startswith("black"):
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))

            # En passant lijevo
            if (r == 3 and self.enPassantPossible == (r - 1, c - 1)):
                if not piecePinned or pinDirection == (-1, -1):
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))

            # En passant desno
            if (r == 3 and self.enPassantPossible == (r - 1, c + 1)):
                if not piecePinned or pinDirection == (-1, 1):
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))

        else:
            # Jedno polje naprijed
            if self.board[r + 1][c] == "--":
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    # Dva polja naprijed
                    if r == 1 and self.board[r + 2][c] == "--":
                        moves.append(Move((r, c), (r + 2, c), self.board))

            # Jedenje lijevo
            if c - 1 >= 0:
                if self.board[r + 1][c - 1].startswith("white"):
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))

            # Jedenje desno
            if c + 1 <= 7:
                if self.board[r + 1][c + 1].startswith("white"):
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))

            # En passant lijevo
            if (r == 4 and self.enPassantPossible == (r + 1, c - 1)):
                if not piecePinned or pinDirection == (1, -1):
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))

            # En passant desno
            if (r == 4 and self.enPassantPossible == (r + 1, c + 1)):
                if not piecePinned or pinDirection == (1, 1):
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))


                    
    # Generiše sve poteze za topa (rook)
    def getRookMoves(self, r, c, moves):
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]  # gore, lijevo, dole, desno
        enemyColor = "black" if self.whiteToMove else "white"
        piecePinned = False
        pinDirection = ()

        # Provjeri da li je figura pinovana
        for i in range(len(self.pins)):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                # ako figura nije kraljica, može se kretati samo u pravcu pina
                if self.board[r][c].split()[1] != "queen":
                    directions = [pinDirection]
                break

        # Istražuje sva polja u datim pravcima
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece.startswith(enemyColor):
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break  # ne može dalje nakon što pojede protivničku figuru
                    else:
                        break  # saveznička figura blokira dalje kretanje
                else:
                    break


    # Generiše sve poteze za skakača (konja)
    def getKnightMoves(self, r, c, moves):
        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                    (1, -2), (1, 2), (2, -1), (2, 1)]  # L-oblik poteza
        allyColor = "white" if self.whiteToMove else "black"

        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if not endPiece.startswith(allyColor):  # može ići ako nije savezničko polje
                    isPinned = False
                    # Konj ne može biti pinovan jer se ne kreće linearno,
                    # ali ovdje ipak provjeravamo u slučaju da je greškom zabilježen
                    for pin in self.pins:
                        if pin[0] == r and pin[1] == c:
                            isPinned = True
                            break
                    if not isPinned:
                        moves.append(Move((r, c), (endRow, endCol), self.board))


    # Generiše sve poteze za lovca (bishop)
    def getBishopMoves(self, r, c, moves):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # dijagonale
        enemyColor = "black" if self.whiteToMove else "white"
        piecePinned = False
        pinDirection = ()

        # Provjeri da li je figura pinovana
        for i in range(len(self.pins)):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                break

        for d in directions:
            # Dozvoli poteze samo u smjeru pina
            if not piecePinned or d == pinDirection or d == (-pinDirection[0], -pinDirection[1]):
                for i in range(1, 8):
                    endRow = r + d[0] * i
                    endCol = c + d[1] * i
                    if 0 <= endRow < 8 and 0 <= endCol < 8:
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece.startswith(enemyColor):
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                    else:
                        break


    # Kraljica kombinira poteze topa i lovca
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)


    # Generiše sve poteze za kralja, uključujući rokadu
    def getKingMoves(self, r, c, moves, includeCastle=True):
        kingMoves = [(-1, -1), (-1, 0), (-1, 1),
                    (0, -1),          (0, 1),
                    (1, -1),  (1, 0), (1, 1)]  # sve susjedne pozicije
        allyColor = "white" if self.whiteToMove else "black"

        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if not endPiece.startswith(allyColor):  # dozvoljeno ako nije savezničko
                    # privremeno pomjeranje kralja na ciljano polje
                    if self.whiteToMove:
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, _, _ = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # vrati kralja nazad na staru poziciju
                    if self.whiteToMove:
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

        # Rokada – dodatna logika ako se traži
        if includeCastle:
            self.getCastleMoves(r, c, moves, allyColor)

                        
    # Funkcija koja dodaje castling poteze ako su dozvoljeni
    def getCastleMoves(self, r, c, moves, allyColor):
        if self.inCheck:
            return  #Rokada nije dozvoljena ako je kralj trenutno pod šahom
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves, allyColor)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves, allyColor)

    # Rokada na kraljevoj strani (short castling)
    def getKingsideCastleMoves(self, r, c, moves, allyColor):
        # Provjerava da li su polja između kralja i topa prazna
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            # Provjera da li ta polja nisu pod napadom
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    # Rokada na kraljičinoj strani (long castling)
    def getQueensideCastleMoves(self, r, c, moves, allyColor):
        # Provjerava da li su polja između kralja i topa prazna
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            # Provjera da li su ta polja bez prijetnji
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))

    # Provjerava da li je dato polje napadnuto od strane protivnika
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # Pretvaramo se da je protivnik na potezu
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # Vraćamo stvarno stanje
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True  # Polje je pod napadom
        return False

class CastleRights:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks  # Bijela rokada desno (king side)
        self.wqs = wqs  # Bijela rokada lijevo (queen side)
        self.bks = bks  # Crna rokada desno
        self.bqs = bqs  # Crna rokada lijevo

class Move():
    # Mape između oznaka na tabli (rank/file) i indeksa liste

    # Redovi (1–8) → indeksi 7–0
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}

    # Inverzna mapa (indeks → oznaka reda)
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    # Kolone (a–h) → indeksi 0–7
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}

    # Inverzna mapa (indeks → oznaka kolone)
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, promotionPiece="queen", isCastleMove=False):
        # Početne i krajnje pozicije
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]

        # Figura koja se pomjera i figura koja je eventualno pojedena
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # En passant logika
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            # Figura koja se zapravo pojede nije na ciljanom polju
            self.pieceCaptured = 'black pawn' if self.pieceMoved.startswith('white') else 'white pawn'

        # Promocija piona
        self.isPawnPromotion = False
        if self.pieceMoved != "--":
            pieceParts = self.pieceMoved.split()
            if len(pieceParts) == 2 and pieceParts[1] == "pawn":
                if (self.pieceMoved.startswith("white") and self.endRow == 0) or \
                   (self.pieceMoved.startswith("black") and self.endRow == 7):
                    self.isPawnPromotion = True
                    self.promotionPiece = promotionPiece  # "queen", "rook", itd.

        # Rokada
        self.isCastleMove = isCastleMove

        # Unikatni ID za potez – olakšava poređenje
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    # Poređenje poteza bazirano na ID-u
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    # Pretvaranje poteza u šahovsku notaciju (npr. e2e4)
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    # Pomoćna funkcija za konverziju koordinata
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
