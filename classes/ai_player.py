import time
import math
import copy
from classes.piece import Pawn

class AI_Player:
    def __init__(self, color, difficulty_level=3):
        self.color = color
        self.difficulty_level = difficulty_level
        self.evaluation_score = 0.0
        self.ai_decision_time = 0.0

        # For checking bonuses
        self.center_squares = {(3,3),(3,4),(4,3),(4,4)}

    def compute_move(self, board):
        start = time.time()
        depth = self.difficulty_level
        alpha = -math.inf
        beta = math.inf
        best_val = -math.inf
        best_move = None

        for move in self._get_all_moves(board.board_state, self.color):
            new_state = self._simulate(board.board_state, move)
            val = self._minimax(new_state, depth - 1, alpha, beta, False)
            if val > best_val:
                best_val = val
                best_move = move
            alpha = max(alpha, best_val)
            if beta <= alpha:
                break

        self.evaluation_score = best_val
        self.ai_decision_time = time.time() - start
        return best_move

    def _minimax(self, board_state, depth, alpha, beta, maximizing):
        if depth == 0:
            return self.evaluate_board(board_state)

        player = self.color if maximizing else ("black" if self.color=="white" else "white")
        moves = self._get_all_moves(board_state, player)
        if not moves:
            return self.evaluate_board(board_state)

        if maximizing:
            value = -math.inf
            for mv in moves:
                child = self._simulate(board_state, mv)
                value = max(value, self._minimax(child, depth-1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = math.inf
            for mv in moves:
                child = self._simulate(board_state, mv)
                value = min(value, self._minimax(child, depth-1, alpha, beta, True))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    def _get_all_moves(self, board_state, color):
        moves = []
        for r in range(8):
            for c in range(8):
                p = board_state[r][c]
                if p and p.color == color:
                    for dest in p.possible_moves(board_state):
                        moves.append(((r,c), dest))
        return moves

    def _simulate(self, board_state, move):
        new_state = copy.deepcopy(board_state)
        (sr,sc), (dr,dc) = move
        piece = new_state[sr][sc]
        new_state[sr][sc] = None
        new_state[dr][dc] = piece
        piece.position = (dr, dc)
        if isinstance(piece, Pawn):
            piece.first_move = False
        return new_state

    def evaluate_board(self, board_state):
        # Base material values
        values = {
            "pawn":    1.0,
            "knight":  3.0,
            "bishop":  3.0,
            "rook":    5.0,
            "queen":   9.0,
            "king":  1000.0
        }

        score = 0.0
        my_moves = 0
        opp_moves = 0

        # count moves for mobility bonus
        for r in range(8):
            for c in range(8):
                p = board_state[r][c]
                if not p: continue
                base = values.get(p.type, 0.0)
                # material
                if p.color == self.color:
                    score += base
                else:
                    score -= base

                # center control bonus
                if (r,c) in self.center_squares:
                    bonus = 0.1
                    score += bonus if p.color==self.color else -bonus

                # mobility count
                moves = p.possible_moves(board_state)
                if p.color == self.color:
                    my_moves += len(moves)
                else:
                    opp_moves += len(moves)

        # mobility effect
        mobility_factor = 0.05
        score += mobility_factor * (my_moves - opp_moves)

        # check bonus for attacking opponent king
        opp_color = "black" if self.color=="white" else "white"
        if self._king_in_check(opp_color, board_state):
            score += 0.5

        return score

    def _king_in_check(self, color, board_state):
        # find king
        kp = None
        for r in range(8):
            for c in range(8):
                p = board_state[r][c]
                if p and p.type=="king" and p.color==color:
                    kp = (r,c)
                    break
            if kp: break
        if not kp:
            return False
        # see if any piece attacks it
        attacker = "black" if color=="white" else "white"
        for r in range(8):
            for c in range(8):
                p = board_state[r][c]
                if p and p.color == attacker and kp in p.possible_moves(board_state):
                    return True
        return False
