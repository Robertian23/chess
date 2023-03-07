import copy, threading

GAME_IN_PLAY = True
move_notation, move_storage = [], []

# CLASSES: BCOLORS, SQUARE, PIECES

class bcolors:
    BOLD = '\033[1m'
    HIGH_BLACK = '\u001b[40m'
    HIGH_WHITE = '\u001b[47m'
    RESET = '\u001b[0m'


class Square:

    def __init__(self, piece, file, rank, occupied = True):
        self.piece = piece
        self.file = file
        self.rank = rank

        if not piece:
            self.occupied = False
        else:
            self.occupied = occupied   
        
        if isinstance(piece, Piece):
            self.symbol = piece.symbol
        else:
            if rank % 2 == 1 and file % 2 == 1 or rank % 2 == 0 and file % 2 == 0:
                self.symbol = "⬛" 
            else:
                self.symbol = "⬜"

    def update_square(self, piece):
        self.piece = piece
        if not self.piece:
            self.occupied = False
        else:
            self.occupied = True 
        
        if isinstance(piece, Piece):
            self.symbol = piece.symbol
        else:
            if self.rank % 2 == 1 and self.file % 2 == 1 or self.rank % 2 == 0 and self.file % 2 == 0:
                self.symbol = "⬛" 
            else:
                self.symbol = "⬜"


class Piece:

    def __init__(self, symbol, name, color):
        self.symbol = symbol
        self.name = name
        self.color = color


class King(Piece):

    def __init__(self, symbol, name, color):
        super().__init__(symbol, name, color)

    def verify_move(self, start_rank, start_file, end_rank, end_file, end_square, board, yes_print):
        for rank in board:
            for square in rank:
                if type(square) is not int and type(square) is not str and isinstance(square.piece, King) and square.piece.color != self.color:
                    if abs(end_rank - square.rank) <= 1 and abs(ord(end_file) - ord(file_labels[square.file])) <= 1:
                        print(abs(end_rank - square.rank), abs(ord(end_file) - square.file)) if yes_print else None
                        print("invalid move: king cannot move next to other king") if yes_print else None
                        return False
        if (start_rank == end_rank and abs(ord(start_file) - ord(end_file)) == 1) or (start_file == end_file and abs(start_rank - end_rank) == 1) or (abs(ord(start_file) - ord(end_file)) == 1 and abs(start_rank - end_rank) == 1):
            if end_square.occupied: 
                return "capture"
            return True
        print("invalid move: king can only move one square vertically, horizontally, or diagonally") if yes_print else None
        return False


class Queen(Piece):

    def __init__(self, symbol, name, color):
        super().__init__(symbol, name, color)   

    def verify_move(self, start_rank, start_file, end_rank, end_file, end_square, board, yes_print):
        try: 
            if start_rank == end_rank or start_file == end_file or abs(start_rank - end_rank) / abs(ord(start_file) - ord(end_file)) == 1:
                for rank in board: 
                    for file in rank:
                        if type(file) is not int and type(file) is not str and start_file != file_labels[file.file] and file is not end_square and file.occupied:
                            if ((end_rank > start_rank and end_rank > file.rank and file.rank > start_rank) or (end_rank < start_rank and end_rank < file.rank and file.rank < start_rank)) and ((ord(end_file) > ord(start_file) and ord(end_file) > ord(file_labels[file.file]) and ord(file_labels[file.file]) > ord(start_file)) or (ord(end_file) < ord(start_file) and ord(end_file) < ord(file_labels[file.file]) and ord(file_labels[file.file]) < ord(start_file))) and abs(start_rank - file.rank) / abs(ord(start_file) - ord(file_labels[file.file])) == 1:
                                print("invalid move: queen is blocked on the diagonal") if yes_print else None
                                return False
                            elif start_file == end_file and file_labels[file.file] == start_file and ((end_rank < start_rank and end_rank < file.rank and file.rank < start_rank) or (start_rank < end_rank and start_rank < file.rank and file.rank < end_rank)):
                                print("invalid move: queen is blocked on the vertical") if yes_print else None
                                return False  
                            elif start_rank == end_rank and file.rank == start_rank and ((ord(end_file) < ord(start_file) and ord(end_file) < ord(file_labels[file.file]) and ord(file_labels[file.file]) < ord(start_file)) or (ord(start_file) < ord(end_file) and ord(start_file) < ord(file_labels[file.file]) and ord(file_labels[file.file]) < ord(end_file))):
                                print("invalid move: queen is blocked on the horizontal") if yes_print else None
                                return False
                if end_square.occupied:
                    return "capture"
                return True
            else:
                print("invalid move: queen must move vertically, horizontally, or diagonally") if yes_print else None
                return False
        except ZeroDivisionError:
            print("invalid move: queen must move vertically, horizontally, or diagonally") if yes_print else None
            return False


class Rook(Piece):

    def __init__(self, symbol, name, color):
        super().__init__(symbol, name, color)

    def verify_move(self, start_rank, start_file, end_rank, end_file, end_square, board, yes_print):
        if start_rank == end_rank or start_file == end_file:
            for rank in board: 
                for file in rank:
                    if type(file) is not int and type(file) is not str and file is not end_square and file.occupied:
                        if start_file == end_file and ((end_rank < start_rank and end_rank < file.rank and file.rank < start_rank) or (start_rank < end_rank and start_rank < file.rank and file.rank < end_rank)):
                            print("invalid move: rook is blocked on the vertical") if yes_print else None
                            return False  
                        elif start_rank == end_rank and ((ord(end_file) < ord(start_file) and ord(end_file) < ord(file_labels[file.file]) and ord(file_labels[file.file]) < ord(start_file)) or (ord(start_file) < ord(end_file) and ord(start_file) < ord(file_labels[file.file]) and ord(file_labels[file.file]) < ord(end_file))):
                            print("invalid move: rook is blocked on the horizontal") if yes_print else None
                            return False
            if end_square.occupied: 
                return "capture"
            return True
        print("invalid move: rook must move vertically or horizontally") if yes_print else None
        return False


class Bishop(Piece):

    def __init__(self, symbol, name, color):
        super().__init__(symbol, name, color)

    def verify_move(self, start_rank, start_file, end_rank, end_file, end_square, board, yes_print):
        try: 
            if abs(start_rank - end_rank) / abs(ord(start_file) - ord(end_file)) == 1:
                for rank in board: 
                    for file in rank:
                        if type(file) is not int and type(file) is not str and start_file != file_labels[file.file] and file is not end_square and file.occupied and ((end_rank > start_rank and end_rank > file.rank and file.rank > start_rank) or (end_rank < start_rank and end_rank < file.rank and file.rank < start_rank)) and ((ord(end_file) > ord(start_file) and ord(end_file) > ord(file_labels[file.file]) and ord(file_labels[file.file]) > ord(start_file)) or (ord(end_file) < ord(start_file) and ord(end_file) < ord(file_labels[file.file]) and ord(file_labels[file.file]) < ord(start_file))) and abs(start_rank - file.rank) / abs(ord(start_file) - ord(file_labels[file.file])) == 1:
                            print("invalid move: bishop is blocked on diagonal") if yes_print else None
                            return False
                if end_square.occupied:
                    return "capture"
                return True
            else:
                print("invalid move: bishop must move diagonally") if yes_print else None
                return False
        except ZeroDivisionError:
            print("invalid move: bishop must move diagonally") if yes_print else None
            return False


class Knight(Piece):

    def __init__(self, symbol, name, color):
        super().__init__(symbol, name, color)

    def verify_move(self, start_rank, start_file, end_rank, end_file, end_square, board, yes_print):
        if (abs(start_rank - end_rank) == 2 and abs(ord(start_file) - ord(end_file)) == 1) or (abs(start_rank - end_rank) == 1 and abs(ord(start_file) - ord(end_file)) == 2):
            if end_square.occupied:
                return "capture"
            return True
        print("invalid move: knight must move in an L shape") if yes_print else None
        return False


class Pawn(Piece):

    def __init__(self, symbol, name, color):
        super().__init__(symbol, name, color)

    def verify_move(self, start_rank, start_file, end_rank, end_file, end_square, board, yes_print):
        if abs(start_rank - end_rank) == 1 and abs(ord(start_file) - ord(end_file)) == 1 and len(move_storage) > 0 and isinstance(move_storage[-1][2], Pawn) and abs(move_storage[-1][5] - move_storage[-1][7]) == 2 and not end_square.occupied: # en passant
            return "capture"
        elif abs(start_rank - end_rank) > 2 or abs(ord(start_file) - ord(end_file)) > 1:
            print("invalid move: move is out of range for pawn") if yes_print else None
            return False
        elif self.color == 'white' and end_rank < start_rank or self.color == 'black' and end_rank > start_rank:
            print("invalid move: pawn cannot move backwards") if yes_print else None
            return False
        elif start_rank == end_rank:
            print("invalid move: pawn cannot move hoirzontally") if yes_print else None
            return False
        elif end_square.occupied and start_file == end_file:
            print("invalid move: square is already occupied by another piece") if yes_print else None
            return False
        elif abs(start_rank - end_rank) >= 1 and start_file != end_file and not end_square.occupied:
            print("invalid move: pawn cannot move diagonally without capturing a piece") if yes_print else None
            return False
        elif abs(start_rank - end_rank) == 2:
            if (self.color == 'white' and start_rank == 2) or (self.color == 'black' and start_rank == 7):
                for rank in board:
                    for file in rank:
                        if type(file) is not int and type(file) is not str:
                            if self.color == 'white' and file.rank == 3 and start_file == file_labels[file.file] and file.occupied:
                                print("invalid move: pawn is blocked") if yes_print else None
                                return False
                            elif self.color == 'black' and file.rank == 6 and start_file == file_labels[file.file] and file.occupied:
                                print("invalid move: pawn is blocked") if yes_print else None
                                return False
                return True
            else:
                print("invalid move: pawn cannot move two squares") if yes_print else None
                return False
        if abs(start_rank - end_rank) == 1 and abs(ord(start_file) - ord(end_file)) == 1 and end_square.occupied:
            return "capture"
        return True

        
# FILE, RANK, PIECE, BOARD SETUP

file_labels = [" ", "a", "b", "c", "d", "e", "f", "g", "h"]
rank_labels = ["1", "2", "3", "4", "5", "6", "7", "8"]

bk = King('♚', 'K', 'black')
bq = Queen('♛', 'Q', 'black')
br1 = Rook('♜', 'R', 'black')
br2 = Rook('♜', 'R', 'black')
bb1 = Bishop('♝', 'B', 'black')
bb2 = Bishop('♝', 'B', 'black')
bn1 = Knight('♞', 'K', 'black')
bn2 = Knight('♞', 'K', 'black')
bp1 = Pawn('♟︎', 'P', 'black')
bp2 = Pawn('♟︎', 'P', 'black')
bp3 = Pawn('♟︎', 'P', 'black')
bp4 = Pawn('♟︎', 'P', 'black')
bp5 = Pawn('♟︎', 'P', 'black')
bp6 = Pawn('♟︎', 'P', 'black')
bp7 = Pawn('♟︎', 'P', 'black')
bp8 = Pawn('♟︎', 'P', 'black')

black_pieces = [bk, bq, br1, br2, bb1, bb2, bn1, bn2, bp1, bp2, bp3, bp4, bp5, bp6, bp7, bp8]
for piece in black_pieces:
    piece.symbol = bcolors.BOLD + piece.symbol + bcolors.RESET

wk = King('♔', 'K', 'white')
wq = Queen('♕', 'Q', 'white')
wr1 = Rook('♖', 'R', 'white')
wr2 = Rook('♖', 'R', 'white')
wb1 = Bishop('♗', 'B', 'white')
wb2 = Bishop('♗', 'B', 'white')
wn1 = Knight('♘', 'N', 'white')
wn2 = Knight('♘', 'N', 'white')
wp1 = Pawn('♙', 'P', 'white')
wp2 = Pawn('♙', 'P', 'white')
wp3 = Pawn('♙', 'P', 'white')
wp4 = Pawn('♙', 'P', 'white')
wp5 = Pawn('♙', 'P', 'white')
wp6 = Pawn('♙', 'P', 'white')
wp7 = Pawn('♙', 'P', 'white')
wp8 = Pawn('♙', 'P', 'white')

board = [[], [], [], [], [], [], [], [], []]

def setup_board(board):
    for r in range(9):
        for f in range(8):
            if f == 0 and r != 8:
                board[r].append(8 - r)
            if r >= 2 and r <= 5: # actual rank 6 through 3, middle rows
                    board[r].append(Square(None, f + 1, 8 - r))
            elif len(board[r]) == 1:
                if r == 0: # actual rank 8, black back row
                    board[r].extend([Square(br1, 1, 8), Square(bn1, 2, 8), Square(bb1, 3, 8), Square(bq, 4, 8), Square(bk, 5, 8), Square(bb2, 6, 8), Square(bn2, 7, 8), Square(br2, 8, 8)])
                if r == 1: # actual rank 7, black front row
                    board[r].extend([Square(bp1, 1, 7), Square(bp2, 2, 7), Square(bp3, 3, 7), Square(bp4, 4, 7), Square(bp5, 5, 7), Square(bp6, 6, 7), Square(bp7, 7, 7), Square(bp8, 8, 7)])
                if r == 6: # actual rank 2, white front row
                    board[r].extend([Square(wp1, 1, 2), Square(wp2, 2, 2), Square(wp3, 3, 2), Square(wp4, 4, 2), Square(wp5, 5, 2), Square(wp6, 6, 2), Square(wp7, 7, 2), Square(wp8, 8, 2)])
                if r == 7: # actual rank 3, white back row
                    board[r].extend([Square(wr1, 1, 1), Square(wn1, 2, 1), Square(wb1, 3, 1), Square(wq, 4, 1), Square(wk, 5, 1), Square(wb2, 6, 1), Square(wn2, 7, 1), Square(wr2, 8, 1)])
        if r == 8: 
            board[r].extend(file_labels)

    # for r in range(9):
    #     for f in range(8):
    #         if f == 0 and r != 8:
    #             board[r].append(8 - r)
    #         if r >= 1 and r <= 6: # actual rank 6 through 3, middle rows
    #                 board[r].append(Square(None, f + 1, 8 - r))
    #         elif len(board[r]) == 1:
    #             if r == 0: # actual rank 8, black back row
    #                 board[r].extend([Square(None, 1, 8), Square(None, 2, 8), Square(None, 3, 8), Square(None, 4, 8), Square(bk, 5, 8), Square(None, 6, 8), Square(None, 7, 8), Square(None, 8, 8)])
    #             if r == 7: # actual rank 3, white back row
    #                 board[r].extend([Square(None, 1, 1), Square(None, 2, 1), Square(None, 3, 1), Square(wq, 4, 1), Square(wk, 5, 1), Square(None, 6, 1), Square(None, 7, 1), Square(None, 8, 1)])
    #     if r == 8: 
    #         board[r].extend(file_labels)
    

# DRAW & FLIP BOARD

def draw_board(board):
    for rank in board:
        for square in rank:
            if isinstance(square, int) or isinstance(square, str):
                print(bcolors.BOLD + str(square) + "  "+ bcolors.RESET, end = '')
            elif square.symbol != '⬛' and square.symbol != '⬜':
                print(square.symbol + "  ", end = '')
            else:
                print(square.symbol + " ", end = '')
        print("\n")
    print("\n")

def flip_board(board):
    file_labels = board.pop(len(board) - 1)
    board = [rank[::-1] for rank in board]
    board = board[::-1]
    for rank in board:
        rank.insert(0, rank.pop(len(rank) - 1))
    board.append([" "] + file_labels[1:len(file_labels)][::-1])
    return board


# BASIC MOVE VALIDATION, CHECK FOR CHECKS, CHECKMATE, STALEMATE
 
def valid_move(start_square, end_square, piece_to_be_moved, piece_to_be_switched, move_color, yes_print):
    if not piece_to_be_moved:
        print("invalid move: there is no piece on selected starting square") if yes_print else None
        return False
    elif piece_to_be_moved.color != move_color:
        print("invalid move: please select a " + move_color + " piece to move") if yes_print else None
        return False
    elif start_square is end_square:
        print("invalid move: piece must move") if yes_print else None
        return False
    elif piece_to_be_switched and piece_to_be_moved.color == piece_to_be_switched.color:
        print("invalid move: cannot move to square with same color piece") if yes_print else None
        return False
    return True

def check_check(board, start_rank, start_file, end_rank, end_file, move_color, yes_print):
    capture = False
    board_copy = copy.deepcopy(board)
    for rank in board_copy:
        for square in rank:
            if type(square) is not int and type(square) is not str and start_rank == square.rank and start_file == file_labels[square.file]:
                piece_to_be_moved = square.piece
                for r in board_copy:
                    for s in r:
                        if type(s) is not int and type(s) is not str and end_rank == s.rank and end_file == file_labels[s.file]:
                            if s.occupied:
                                capture = True
                            piece_to_be_switched = s.piece
                            s.update_square(piece_to_be_moved)
                if capture:
                    square.update_square(None)
                else: 
                    square.update_square(piece_to_be_switched)

    for rank in board_copy:
        for square in rank:
            if type(square) is not int and type(square) is not str and square.piece:
                piece_to_be_moved = square.piece
                for r in board_copy:
                    for s in r:
                        if type(s) is not int and type(s) is not str:
                            piece_to_be_switched = s.piece
                            valid = valid_move(square, s, piece_to_be_moved, piece_to_be_switched, piece_to_be_moved.color, False)
                            if valid: 
                                verify = piece_to_be_moved.verify_move(square.rank, file_labels[square.file], s.rank, file_labels[s.file], s, board_copy, False)
                            if valid and verify and s.piece and isinstance(s.piece, King):
                                if s.piece.color == move_color:
                                    print("invalid move: " + s.piece.color + " king is in check!") if yes_print else None
                                    return "invalid check"
                                else:
                                    print("check!") if yes_print else None
                                    return "valid check"
    return False

def check_mates(board, start_rank, start_file, end_rank, end_file, move_color):
    # intended move is played in the future on a copy of board
    capture = False
    board_copy = copy.deepcopy(board)
    for rank in board_copy:
        for square in rank:
            if type(square) is not int and type(square) is not str and start_rank == square.rank and start_file == file_labels[square.file]:
                piece_to_be_moved = square.piece
                for r in board_copy:
                    for s in r:
                        if type(s) is not int and type(s) is not str and end_rank == s.rank and end_file == file_labels[s.file]:
                            if s.occupied:
                                capture = True
                            piece_to_be_switched = s.piece
                            s.update_square(piece_to_be_moved)
                if capture:
                    square.update_square(None)
                else: 
                    square.update_square(piece_to_be_switched)

    # test all possible moves and see if they lead to check
    checkmate_moves, stalemate_moves = 0, 0
    mate = None
    for rank in board_copy:
        for square in rank:
            if type(square) is not int and type(square) is not str and square.piece and square.piece.color != move_color:
                piece_to_be_moved = square.piece
                for r in board_copy:
                    for s in r:
                        if type(s) is not int and type(s) is not str:
                            piece_to_be_switched = s.piece
                            valid = valid_move(square, s, piece_to_be_moved, piece_to_be_switched, piece_to_be_moved.color, False)
                            if valid: 
                                verify = piece_to_be_moved.verify_move(square.rank, file_labels[square.file], s.rank, file_labels[s.file], s, board_copy, False)
                            if valid and verify:
                                mate = check_check(board_copy, square.rank, file_labels[square.file], s.rank, file_labels[s.file], piece_to_be_moved.color, False)
                            if valid and verify and mate != "invalid check" or mate != None:
                                if check_check(board, start_rank, start_file, end_rank, end_file, move_color, False) != "valid check" and isinstance(square.piece, King):
                                    checkmate_moves += 1
                                else:
                                    stalemate_moves += 1
    if checkmate_moves == 0:
        print(move_color + " wins by checkmate")
        return "checkmate"
    elif stalemate_moves == 0:
        print("draw by stalemate")
        return "stalemate"
    else:
        return False


# RECORD MOVES

def record_move(move_number, squares_pieces, moves, verifications):
    start_square, end_square, piece_to_be_moved, piece_to_be_switched = squares_pieces[0], squares_pieces[1], squares_pieces[2], squares_pieces[3]
    capture_occurred, check_occurred = verifications[0], verifications[1]
    sf, sr, ef, er = moves[0], moves[1], moves[2], moves[3]
    move_storage.append(squares_pieces + moves)
    symbol, cap_oc, ch_oc = "", "", ""
    if not isinstance(piece_to_be_moved, Pawn):
        print("piece: ", piece_to_be_moved)
        symbol = piece_to_be_moved.symbol
    if capture_occurred:
        cap_oc = "x"
    if check_occurred == "valid check":
        ch_oc = "+"
    if len(move_notation) >= move_number and str(move_number) == move_notation[move_number - 1][0][0]:
        move_notation[move_number - 1] += ["  " + symbol + " " + cap_oc + ef + str(er) + ch_oc]
    else:
        move_notation.append([str(move_number) + ". " + symbol + " " + cap_oc + ef + str(er) + ch_oc]) 
    for move in move_notation:
        if len(move) == 2:
            print(move[0] + move[1] + "\n")
        else:
            print(move[0] + "\n")



# MOVE PIECE

def move_piece(move, board, move_color):
    squares_pieces = [None, None, None, None]
    if len(move) != 5:
        print("incorrect move format: please enter starting and ending square separated by a space (e.g. e2 e4)")
        return squares_pieces, [None, None, None, None], [None, None, None]
    capture_occurred, check, mates = False, False, False
    start, end = move[:2], move[3:]
    start_rank, start_file, end_rank, end_file = int(start[1]), start[0], int(end[1]), end[0]
    for rank in board:
        for square in rank:
            if type(square) is not int and type(square) is not str and start_rank == square.rank and start_file == file_labels[square.file]:
                piece_to_be_moved = square.piece
                for r in board:
                    for s in r:
                        if type(s) is not int and type(s) is not str and end_rank == s.rank and end_file == file_labels[s.file]:
                            piece_to_be_switched = s.piece
                            valid = valid_move(square, s, piece_to_be_moved, piece_to_be_switched, move_color, True)
                            if valid: 
                                verify = piece_to_be_moved.verify_move(start_rank, start_file, end_rank, end_file, s, board, True)
                            if valid and verify:
                                check = check_check(board, start_rank, start_file, end_rank, end_file, move_color, True)
                                mates = check_mates(board, start_rank, start_file, end_rank, end_file, move_color) if check else None
                            if not valid or not verify or check == "invalid check": 
                                piece_to_be_moved = None
                            else:
                                s.update_square(piece_to_be_moved)
                            squares_pieces = [square, s, piece_to_be_moved, piece_to_be_switched]
                if valid and verify == "capture":
                    square.update_square(None)
                    capture_occurred = True
                elif valid and verify and check != "invalid check": 
                    square.update_square(piece_to_be_switched)
    moves, verifications = [start_file, start_rank, end_file, end_rank], [capture_occurred, check, mates]
    return squares_pieces, moves, verifications
                        
def undo_move(move_notation, move_storage):

    last_move = move_storage[-1]
    start_square, end_square, piece_to_be_moved, piece_to_be_switched = last_move[0], last_move[1], last_move[2], last_move[3]

    start_square.update_square(piece_to_be_moved)
    end_square.update_square(piece_to_be_switched)

    move_notation[-1].pop()
    move_storage.pop()

# GAME PLAY                     

def play(board, GAME_IN_PLAY, move_notation, move_storage): 
    
    move_number = 1

    setup_board(board)
    draw_board(board)   

    
    while GAME_IN_PLAY:

        # white's move
        wp, mate_oc, white_move = None, False, False
        while not wp and not mate_oc and white_move != "undo": 
            white_move = input("white's move: start square, end square: ")
            if white_move == "undo":
                if move_number != 1:
                    undo_move(move_notation, move_storage)
                    move_number -= 1
                    break
                else:
                    print("cannot undo on first move")
                    white_move = False
            else:
                wps, wms, wvs = move_piece(white_move, board, "white")
                wp, mate_oc = wps[2], wvs[2]
        if white_move != "undo" and wp:
            record_move(move_number, wps, wms, wvs)
        
        board = flip_board(board)
        draw_board(board)

        if mate_oc:
            break

        # black's move
        bp, black_move = None, False
        while not bp and not mate_oc and black_move != "undo": 
            black_move = input("black's move: start square, end square: ")
            if black_move == "undo":
                undo_move(move_notation, move_storage)
            else:
                bps, bms, bvs = move_piece(black_move, board, "black")
                bp, mate_oc = bps[2], bvs[2]
        if black_move != "undo" and wp:
            record_move(move_number, bps, bms, bvs)

        board = flip_board(board)
        draw_board(board)  
        
        GAME_IN_PLAY = not mate_oc
        move_number += 1

play(board, GAME_IN_PLAY, move_notation, move_storage)


# verify piece move, blocked
# verify check, checkmate, stalemate
# verify pin
# verify capture

# castling
# en passant
# pawn promotion

