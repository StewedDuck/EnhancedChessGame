import pygame, sys, os
from classes.piece import Pawn, Rook, Knight, Bishop, Queen, King

class Board:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.square_size = width // 8
        self.board_state = [[None]*8 for _ in range(8)]
        self.piece_images = {}
        self.load_assets()

    def load_assets(self):
        # board bg
        try:
            bg = pygame.image.load(os.path.join("assets","board.png"))
            self.board_image = pygame.transform.scale(bg,(self.width,self.height))
        except Exception as e:
            print("Board load error:", e); sys.exit()

        # piece PNGs
        for kind in ("bishop","king","knight","pawn","queen","rook"):
          for col in ("black","white"):
            key = f"chess-{kind}-{col}"
            path = os.path.join("assets", f"{key}.png")
            img = pygame.image.load(path)
            img = pygame.transform.scale(img,(self.square_size,self.square_size))
            self.piece_images[key] = img

    def initialize_board(self):
        # Top row (black)
        back = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for c,cls in enumerate(back):
            self.board_state[0][c] = cls("black",(0,c))
            self.board_state[1][c] = Pawn("black",(1,c))
        # empty
        for r in range(2,6):
            for c in range(8):
                self.board_state[r][c] = None
        # white pawns & back row
        for c in range(8):
            self.board_state[6][c] = Pawn("white",(6,c))
        back_w = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for c,cls in enumerate(back_w):
            self.board_state[7][c] = cls("white",(7,c))

    def draw_board(self):
        # background
        self.screen.blit(self.board_image,(0,0))
        # pieces
        for r in range(8):
            for c in range(8):
                p = self.board_state[r][c]
                if not p: continue
                x, y = c*self.square_size, r*self.square_size
                img = self.piece_images[p.image_key]
                self.screen.blit(img,(x,y))

    def get_board_pos(self, mouse_pos):
        x,y = mouse_pos
        return y//self.square_size, x//self.square_size
