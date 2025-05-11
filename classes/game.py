import pygame
import copy
import os
import csv
import statistics
from classes.ui import SideMenu
from classes.board import Board
from classes.piece import Pawn, Rook, Knight, Bishop, Queen, King
from classes.ai_player import AI_Player

class Game:
    def __init__(self, screen, board_w, board_h, menu_w):
        self.screen = screen
        self.board_w = board_w
        self.board_h = board_h
        self.menu_w = menu_w

        # UI
        self.menu = SideMenu(self.board_w, self.menu_w, self.board_h)
        self.board_offset_x = 0
        self.board = Board(screen, self.board_w, self.board_h)

        # Game state
        self.mode = "1v1"             # "1v1" or "ai"
        self.active_player = "white"
        self.state = "ongoing"        # "ongoing", "checkmate", "stalemate"
        self.winner = None
        self.paused = False

        # Selection & animations
        self.selected_pos = None
        self.hover_target = None
        self.last_hover_target = None
        self.hover_frames = 0
        self.max_hover = 15
        self.hover_height = 20
        self.click_anim = False
        self.click_offset = 0
        self.click_dir = -1

        # Promotion
        self.promote = False
        self.promote_pos = None
        self.promote_color = None
        self.promote_rects = []

        # AI
        self.ai = AI_Player("black")
        self.waiting_for_ai = False
        self.ai_thinking = False

        # Clocks (5 minutes each)
        self.time_limit = 5 * 60
        self.clock_times = {"white": self.time_limit, "black": self.time_limit}
        self.last_tick = pygame.time.get_ticks()

        # Logging fields
        self.move_count    = 0
        self.move_times    = []
        self.last_move_ts  = self.last_tick
        self.captures      = 0
        self.game_start_ts = self.last_tick
        self.ai_times      = []

    def start_game(self):
        self.board.initialize_board()
        self.active_player = "white"
        self.state = "ongoing"
        self.winner = None
        self.paused = False
        self.selected_pos = None
        self.promote = False
        self.waiting_for_ai = False
        self.ai_thinking = False
        self.clock_times = {"white": self.time_limit, "black": self.time_limit}
        self.last_tick = pygame.time.get_ticks()

        # Reset animations
        self.hover_target = None
        self.last_hover_target = None
        self.hover_frames = 0
        self.click_anim = False
        self.click_offset = 0
        self.click_dir = -1

        # Reset logging
        now = self.last_tick
        self.move_count    = 0
        self.move_times.clear()
        self.last_move_ts  = now
        self.captures      = 0
        self.game_start_ts = now
        self.ai_times.clear()

    def update_game(self):
        now = pygame.time.get_ticks()
        dt = (now - self.last_tick) / 1000.0

        # Tick clocks if not AI-thinking, paused, or promoting
        if (self.state == "ongoing"
                and not self.paused
                and not self.promote
                and not (self.waiting_for_ai and self.ai_thinking)):
            self.clock_times[self.active_player] -= dt
            if self.clock_times[self.active_player] <= 0:
                self.state = "checkmate"
                self.winner = "black" if self.active_player == "white" else "white"

        self.last_tick = now

        # update click-float
        if self.click_anim:
            self.click_offset += self.click_dir
            if self.click_offset <= -3 or self.click_offset >= 3:
                self.click_dir *= -1

        # DRAWING
        self.screen.fill((50, 50, 50))
        self.screen.blit(self.board.board_image, (self.board_offset_x, 0))

        # Blink king in check
        if self.state == "ongoing" and self._is_in_check(self.active_player, self.board.board_state):
            if (now // 300) % 2 == 0:
                kr, kc = self._find_king(self.active_player, self.board.board_state)
                sz = self.board.square_size
                ov = pygame.Surface((sz, sz), pygame.SRCALPHA)
                ov.fill((255, 0, 0, 100))
                self.screen.blit(ov, (self.board_offset_x + kc*sz, kr*sz))

        # Detect checkmate/stalemate
        if self.state == "ongoing" and not self.promote and not (self.waiting_for_ai and not self.ai_thinking):
            in_chk = self._is_in_check(self.active_player, self.board.board_state)
            can_mv = self._has_any_valid_move(self.active_player)
            if in_chk and not can_mv:
                self.state = "checkmate"
                self.winner = "black" if self.active_player == "white" else "white"
            elif not in_chk and not can_mv:
                self.state = "stalemate"

        # Endgame: log stats, display message, then return
        if self.state in ("checkmate", "stalemate"):
            path = "stats.csv"
            write_header = not os.path.exists(path) or os.path.getsize(path) == 0
            with open(path, "a", newline="") as f:
                w = csv.writer(f)
                if write_header:
                    w.writerow([
                        "move_count", "avg_move_time", "min_move_time", "max_move_time", "sd_move_time",
                        "captures", "game_duration", "avg_ai_time"
                    ])
                # compute stats
                avg_m = statistics.mean(self.move_times) if self.move_times else 0
                mn = min(self.move_times) if self.move_times else 0
                mx = max(self.move_times) if self.move_times else 0
                sd = statistics.pstdev(self.move_times) if len(self.move_times) > 1 else 0
                duration = (pygame.time.get_ticks() - self.game_start_ts) / 1000.0
                avg_ai = statistics.mean(self.ai_times) if self.ai_times else 0
                w.writerow([
                    self.move_count,
                    f"{avg_m:.2f}", f"{mn:.2f}", f"{mx:.2f}", f"{sd:.2f}",
                    self.captures,
                    f"{duration:.2f}",
                    f"{avg_ai:.2f}"
                ])

            # endgame text
            font = pygame.font.SysFont(None, 64)
            msg = "Stalemate" if self.state == "stalemate" else f"{self.winner.capitalize()} wins!"
            txt = font.render(msg, True, (255, 255, 255))
            rect = txt.get_rect(center=(self.board_w//2, self.board_h//2))
            self.screen.blit(txt, rect)
            self.menu.draw(self.screen, self)
            return

        # Promotion UI
        if self.promote:
            self._draw_promotion_ui()
            return

        # Draw pieces with animations
        for r in range(8):
            for c in range(8):
                p = self.board.board_state[r][c]
                if not p:
                    continue
                x = self.board_offset_x + c*self.board.square_size
                y = r*self.board.square_size

                # hover jump
                if self.hover_target == (r, c) and self.hover_frames > 0:
                    frac = self.hover_frames / self.max_hover
                    y += int(-self.hover_height * frac)
                    self.hover_frames -= 1

                # click float
                if self.click_anim and self.selected_pos == (r, c):
                    y += self.click_offset

                img = self.board.piece_images[p.image_key]
                self.screen.blit(img, (x, y))

        # Highlight & valid moves
        if self.selected_pos:
            self._draw_selection_and_moves()

        # Sidebar
        self.menu.draw(self.screen, self)
        # End DRAWING

        # Handle AI two-phase move
        if self.waiting_for_ai and not self.ai_thinking:
            self.ai_thinking = True
            return

        if self.waiting_for_ai and self.ai_thinking:
            start = pygame.time.get_ticks()
            mv = self.ai.compute_move(self.board)
            think_time = (pygame.time.get_ticks() - start) / 1000.0
            self.clock_times[self.ai.color] -= think_time
            self.ai_times.append(think_time)

            if mv:
                (sr, sc), (dr, dc) = mv
                pc = self.board.board_state[sr][sc]
                self.board.board_state[sr][sc] = None
                self.board.board_state[dr][dc] = pc
                pc.position = (dr, dc)

            self.active_player = "white"
            self.waiting_for_ai = False
            self.ai_thinking = False
            self.last_tick = pygame.time.get_ticks()

    def process_input(self, event):
        # Sidebar
        if self.menu.handle_event(event, self):
            return

        # Hover once only
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            new_target = None
            if self.board_offset_x <= mx < self.board_offset_x + self.board_w:
                bx = mx - self.board_offset_x
                row, col = self.board.get_board_pos((bx, my))
                p = self.board.board_state[row][col]
                if p and p.color == self.active_player:
                    new_target = (row, col)
            if new_target != self.last_hover_target:
                self.hover_target = new_target
                if new_target is not None:
                    self.hover_frames = self.max_hover
                self.last_hover_target = new_target
            return

        # check/stalemate
        if (self.state in ("checkmate", "stalemate")
                or self.promote
                or self.paused
                or self.waiting_for_ai):
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if not (self.board_offset_x <= mx < self.board_offset_x + self.board_w):
                return
            bx = mx - self.board_offset_x
            row, col = self.board.get_board_pos((bx, my))

            # Select
            if not self.selected_pos:
                p = self.board.board_state[row][col]
                if p and p.color == self.active_player:
                    self.selected_pos = (row, col)
                    self.click_anim = True
                    self.click_offset = 0
                    self.click_dir = -1
                return

            # Attempt move
            sr, sc = self.selected_pos
            valid = self._calc_valid_moves(sr, sc)
            if (row, col) in valid:
                # count captures
                target_piece = self.board.board_state[row][col]
                if target_piece:
                    self.captures += 1

                # commit move
                piece = self.board.board_state[sr][sc]
                self.board.board_state[sr][sc] = None
                self.board.board_state[row][col] = piece
                piece.position = (row, col)

                # log move time
                now = pygame.time.get_ticks()
                elapsed = (now - self.last_move_ts) / 1000.0
                self.move_times.append(elapsed)
                self.move_count += 1
                self.last_move_ts = now

                # pawn promotion
                if isinstance(piece, Pawn):
                    if piece.first_move:
                        piece.first_move = False
                    if row in (0, 7):
                        self.promote = True
                        self.promote_pos = (row, col)
                        self.promote_color = piece.color
                        self.selected_pos = None
                        return

                # switch turn
                if self.mode == "ai":
                    self.active_player = self.ai.color
                    self.waiting_for_ai = True
                    self.ai_thinking = False
                else:
                    self.active_player = "black" if self.active_player == "white" else "white"
                self.last_tick = pygame.time.get_ticks()

            # clear selection
            self.selected_pos = None
            self.click_anim = False
            self.click_offset = 0

    # Helpers

    def _draw_selection_and_moves(self):
        sr, sc = self.selected_pos
        rect = pygame.Rect(
            self.board_offset_x + sc*self.board.square_size,
            sr*self.board.square_size,
            self.board.square_size, self.board.square_size
        )
        pygame.draw.rect(self.screen, (255, 0, 0), rect, 3)

        piece = self.board.board_state[sr][sc]
        cand = piece.possible_moves(self.board.board_state)

        # Castling
        if isinstance(piece, King) and piece.first_move and not self._is_in_check(self.active_player, self.board.board_state):
            rook = self.board.board_state[sr][7]
            if isinstance(rook, Rook) and rook.first_move and all(self.board.board_state[sr][i] is None for i in (5,6)):
                cand.append((sr, 6))
            rook = self.board.board_state[sr][0]
            if isinstance(rook, Rook) and rook.first_move and all(self.board.board_state[sr][i] is None for i in (1,2,3)):
                cand.append((sr, 2))

        valid = []
        for vr, vc in cand:
            tgt = self.board.board_state[vr][vc]
            if tgt and tgt.type == "king":
                continue
            tmp = copy.deepcopy(self.board.board_state)
            tp = tmp[sr][sc]
            tmp[sr][sc] = None
            tmp[vr][vc] = tp
            if isinstance(tp, Pawn):
                tp.first_move = False
            if not self._is_in_check(self.active_player, tmp):
                valid.append((vr, vc))

        for vr, vc in valid:
            cx = self.board_offset_x + vc*self.board.square_size + self.board.square_size//2
            cy = vr*self.board.square_size + self.board.square_size//2
            pygame.draw.circle(self.screen, (0, 255, 0), (cx, cy), 10)

    def _calc_valid_moves(self, sr, sc):
        piece = self.board.board_state[sr][sc]
        cand = piece.possible_moves(self.board.board_state)
        # Castling logic
        valid = []
        for vr, vc in cand:
            tgt = self.board.board_state[vr][vc]
            if tgt and tgt.type == "king":
                continue
            tmp = copy.deepcopy(self.board.board_state)
            tp = tmp[sr][sc]
            tmp[sr][sc] = None
            tmp[vr][vc] = tp
            if isinstance(tp, Pawn):
                tp.first_move = False
            if not self._is_in_check(self.active_player, tmp):
                valid.append((vr, vc))
        return valid

    def _draw_promotion_ui(self):
        overlay = pygame.Surface((self.board_w + self.menu_w, self.board_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        size = int(self.board.square_size * 1.5)
        cx = self.board_offset_x + self.board_w // 2
        cy = self.board_h // 2
        self.promote_rects = []
        for i, cls in enumerate((Queen, Rook, Bishop, Knight)):
            key = f"chess-{cls.__name__.lower()}-{self.promote_color}"
            img = pygame.transform.scale(self.board.piece_images[key], (size, size))
            rect = img.get_rect(center=(cx + (i - 1.5) * size * 1.1, cy))
            self.screen.blit(img, rect)
            self.promote_rects.append(rect)

    def _find_king(self, color, board_state):
        for r in range(8):
            for c in range(8):
                p = board_state[r][c]
                if p and p.type == "king" and p.color == color:
                    return (r, c)
        return None

    def _is_in_check(self, color, board_state):
        king_pos = self._find_king(color, board_state)
        if not king_pos:
            return False
        opp = "black" if color == "white" else "white"
        for r in range(8):
            for c in range(8):
                p = board_state[r][c]
                if p and p.color == opp and king_pos in p.possible_moves(board_state):
                    return True
        return False

    def _has_any_valid_move(self, color):
        for r in range(8):
            for c in range(8):
                p = self.board.board_state[r][c]
                if p and p.color == color:
                    for mv in p.possible_moves(self.board.board_state):
                        tgt = self.board.board_state[mv[0]][mv[1]]
                        if tgt and tgt.type == "king":
                            continue
                        tmp = copy.deepcopy(self.board.board_state)
                        tp = tmp[r][c]
                        tmp[r][c] = None
                        tmp[mv[0]][mv[1]] = tp
                        if isinstance(tp, Pawn):
                            tp.first_move = False
                        if not self._is_in_check(color, tmp):
                            return True
        return False
