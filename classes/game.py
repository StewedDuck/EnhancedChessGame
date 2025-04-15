import pygame
from classes.board import Board
from classes.piece import Pawn


class Game:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.state = "ongoing"
        self.active_player = "white"
        self.board = Board(self.screen, width, height)
        self.selected_pos = None  # (row, col) of currently selected piece

    def start_game(self):
        self.board.initialize_board()

    def update_game(self):
        self.screen.fill((0, 0, 0))
        self.board.draw_board()

        # draw a red border on the selected piece
        if self.selected_pos is not None:
            row, col = self.selected_pos
            rect = pygame.Rect(col * self.board.square_size, row * self.board.square_size,
                               self.board.square_size, self.board.square_size)
            pygame.draw.rect(self.screen, (255, 0, 0), rect, 3)

            # retrieve the selected piece object
            piece_obj = self.board.board_state[row][col]
            if piece_obj is not None:
                valid_moves = piece_obj.possible_moves(self.board.board_state)

                # draw a small green circle where the piece can move.
                for move_row, move_col in valid_moves:
                    center_x = int(move_col * self.board.square_size + self.board.square_size / 2)
                    center_y = int(move_row * self.board.square_size + self.board.square_size / 2)
                    pygame.draw.circle(self.screen, (0, 255, 0), (center_x, center_y), 10)

    def process_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            row, col = self.board.get_board_pos(mouse_pos)

            if self.selected_pos is None:
                # only select the piece if it exists and its color matches the active player
                piece = self.board.board_state[row][col]
                if piece is not None and piece.color == self.active_player:
                    self.selected_pos = (row, col) # allow picking after checking
            else:
                src_row, src_col = self.selected_pos #just in case
                piece_obj = self.board.board_state[src_row][src_col]
                valid_moves = piece_obj.possible_moves(self.board.board_state)
                if (row, col) in valid_moves:
                    target = self.board.board_state[row][col]
                    if target is not None and target.color != self.active_player:
                        print(f"{target.type} captured!")
                    # move the piece
                    piece_obj.position = (row, col)
                    self.board.board_state[row][col] = piece_obj
                    self.board.board_state[src_row][src_col] = None
                    # for pawn first move
                    if piece_obj.type == "pawn":
                        piece_obj.first_move = False
                    # Switch turns
                    if self.active_player == "white":
                        self.active_player = "black"
                    else:
                        self.active_player = "white"
                else:
                    print("Invalid move")
                self.selected_pos = None #clear selection


