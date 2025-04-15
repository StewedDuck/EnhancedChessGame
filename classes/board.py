import pygame
import sys
import os
from classes.piece import Piece, Pawn, Knight, Bishop, Rook, Queen, King

class Board:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.square_size = width // 8
        self.board_state = [[None for _ in range(8)] for _ in range(8)]  # 8x8 board (repr as 8x8 list)
        self.piece_images = {}
        self.load_assets()

    def load_assets(self):
        # Load board
        try:
            board_path = os.path.join("assets", "board.png")
            self.board_image = pygame.image.load(board_path)
            self.board_image = pygame.transform.scale(self.board_image, (self.width, self.height))
        except Exception as e:
            print("Error loading board image:", e)
            sys.exit()

        # Load piece
        piece_file_names = [
            "chess-bishop-black", "chess-bishop-white",
            "chess-king-black", "chess-king-white",
            "chess-knight-black", "chess-knight-white",
            "chess-pawn-black", "chess-pawn-white",
            "chess-queen-black", "chess-queen-white",
            "chess-rook-black", "chess-rook-white"
        ]
        try:
            for name in piece_file_names:
                path = os.path.join("assets", name + ".png")
                image = pygame.image.load(path)
                image = pygame.transform.scale(image, (self.square_size, self.square_size))
                self.piece_images[name] = image
        except Exception as e:
            print("Error loading piece images:", e)
            sys.exit()

    # set board
    def initialize_board(self):
        self.board_state = [
            # Black's back (row 0)
            [
                Rook("black", (0, 0)),
                Knight("black", (0, 1)),
                Bishop("black", (0, 2)),
                Queen("black", (0, 3)),
                King("black", (0, 4)),
                Bishop("black", (0, 5)),
                Knight("black", (0, 6)),
                Rook("black", (0, 7))
            ],
            # Black's pawns (row 1)
            [Pawn("black", (1, col)) for col in range(8)],
            # Empty rows (rows 2-5)
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            # White's pawns (row 6)
            [Pawn("white", (6, col)) for col in range(8)],
            # White's back (row 7)
            [
                Rook("white", (7, 0)),
                Knight("white", (7, 1)),
                Bishop("white", (7, 2)),
                Queen("white", (7, 3)),
                King("white", (7, 4)),
                Bishop("white", (7, 5)),
                Knight("white", (7, 6)),
                Rook("white", (7, 7))
            ]
        ]

    def draw_board(self):
        self.screen.blit(self.board_image, (0, 0))
        # draw pieces
        for row in range(8):
            for col in range(8):
                piece_obj = self.board_state[row][col]
                if piece_obj:
                    image_key = piece_obj.image_key
                    pos_x = col * self.square_size
                    pos_y = row * self.square_size
                    self.screen.blit(self.piece_images[image_key], (pos_x, pos_y))

    def get_board_pos(self, mouse_pos):
        x, y = mouse_pos
        row = y // self.square_size
        col = x // self.square_size
        return row, col
