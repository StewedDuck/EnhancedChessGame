class Piece:
    def __init__(self, piece_type, color, position):
        self.type = piece_type
        self.color = color      # white or black
        self.position = position  # (row, col)
        self.image_key = f"chess-{piece_type}-{color}"

    def move(self, new_position):
        self.position = new_position

    def validate_move(self, new_position, board_state):
        return True

    def capture(self, target_piece):
        pass

    def possible_moves(self, board_state): # just in case
        return []


class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__("pawn", color, position)
        self.first_move = True

    def possible_moves(self, board_state):
        moves = []
        row, col = self.position
        # White pawns move up, black pawns move down
        direction = -1 if self.color == "white" else 1

        # forward move
        # one square forward
        new_row = row + direction
        if 0 <= new_row < 8 and board_state[new_row][col] is None:
            moves.append((new_row, col))

            # Two squares forward
            if self.first_move:
                new_row2 = row + 2 * direction
                if 0 <= new_row2 < 8 and board_state[new_row2][col] is None:
                    moves.append((new_row2, col))

        # capturing move
        # left
        new_col = col - 1
        if new_col >= 0 and 0 <= new_row < 8:
            target = board_state[new_row][new_col]
            if target is not None and target.color != self.color:
                moves.append((new_row, new_col))

        # right
        new_col = col + 1
        if new_col < 8 and 0 <= new_row < 8:
            target = board_state[new_row][new_col]
            if target is not None and target.color != self.color:
                moves.append((new_row, new_col))

        return moves

class Knight(Piece):
    def __init__(self, color, position):
        super().__init__("knight", color, position)

    def possible_moves(self, board_state):
        moves = []
        row, col = self.position
        # moves in an "L" shape with 8 possible offsets:
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            new_row = row + dr
            new_col = col + dc
            # check if the move will be in the board
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board_state[new_row][new_col]
                # capturing
                if target is None or target.color != self.color:
                    moves.append((new_row, new_col))
        return moves

class Bishop(Piece):
    def __init__(self, color, position):
        super().__init__("bishop", color, position)

    def possible_moves(self, board_state):
        moves = []
        row, col = self.position
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            # loop until out of board or a met with piece
            while 0 <= r < 8 and 0 <= c < 8:
                target = board_state[r][c]
                if target is None: # empty square, add move and continue checking
                    moves.append((r, c))
                elif target.color != self.color: # opponent piece, add move and stop
                    moves.append((r, c))
                    break
                else:
                    # own piece so stop
                    break
                r += dr
                c += dc
        return moves


class Rook(Piece):
    def __init__(self, color, position):
        super().__init__("rook", color, position)

    def possible_moves(self, board_state):
        moves = []
        row, col = self.position

        # left
        for c in range(col - 1, -1, -1):
            target = board_state[row][c]
            if target is None:
                moves.append((row, c))
            elif target.color != self.color:
                moves.append((row, c))
                break
            else:
                break

        # right
        for c in range(col + 1, 8):
            target = board_state[row][c]
            if target is None:
                moves.append((row, c))
            elif target.color != self.color:
                moves.append((row, c))
                break
            else:
                break

        # upward
        for r in range(row - 1, -1, -1):
            target = board_state[r][col]
            if target is None:
                moves.append((r, col))
            elif target.color != self.color:
                moves.append((r, col))
                break
            else:
                break

        # downward
        for r in range(row + 1, 8):
            target = board_state[r][col]
            if target is None:
                moves.append((r, col))
            elif target.color != self.color:
                moves.append((r, col))
                break
            else:
                break

        return moves

class Queen(Piece):
    def __init__(self, color, position):
        super().__init__("queen", color, position)

    def possible_moves(self, board_state):
        moves = []
        row, col = self.position
        directions = [
            (-1, 0),  # Up
            (1, 0),   # Down
            (0, -1),  # Left
            (0, 1),   # Right
            (-1, -1), # Up-Left
            (-1, 1),  # Up-Right
            (1, -1),  # Down-Left
            (1, 1)    # Down-Right
        ]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board_state[r][c]
                if target is None:  # empty square, add move and continue checking
                    moves.append((r, c))
                elif target.color != self.color:  # opponent piece, add move and stop
                    moves.append((r, c))
                    break
                else: # own piece
                    break
                r += dr
                c += dc
        return moves

class King(Piece):
    def __init__(self, color, position):
        super().__init__("king", color, position)

    def possible_moves(self, board_state):
        moves = []
        row, col = self.position
        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            ( 0, -1),
            ( 0, 1),
            ( 1, -1),
            ( 1, 0),
            ( 1, 1)
        ]
        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board_state[new_row][new_col]
                if target is None or target.color != self.color:
                    moves.append((new_row, new_col))

        # castling move here (still figuring how)
        return moves
