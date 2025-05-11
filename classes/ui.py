import pygame

class SideMenu:
    def __init__(self, board_width, menu_width, screen_height):
        # size & position
        self.width = menu_width
        self.height = screen_height
        self.x_offset = board_width

        # fonts
        self.font_large = pygame.font.SysFont(None, 28)
        self.font_small = pygame.font.SysFont(None, 20)

        # buttons: mode, difficulty, and others
        labels = [
            "Mode: 1v1",
            "Mode: vs AI",
            "Easy",
            "Medium",
            "Hard",
            "Pause",
            "Restart",
            "Quit"
        ]
        self.buttons = {}
        for i, label in enumerate(labels):
            rect = pygame.Rect(self.x_offset + 10, 200 + i*45, self.width - 20, 40)
            self.buttons[label] = rect

    def draw(self, screen, game):
        # background panel
        panel = pygame.Surface((self.width, self.height))
        panel.fill((50, 50, 50))
        screen.blit(panel, (self.x_offset, 0))

        # turn indicator
        turn_txt = self.font_large.render(
            f"Turn: {game.active_player.capitalize()}", True, (255,255,255)
        )
        screen.blit(turn_txt, (self.x_offset + 10, 10))

        # clocks
        for i, color in enumerate(("black", "white")):
            secs = max(0, int(game.clock_times[color]))
            m, s = divmod(secs, 60)
            lbl = f"{color.capitalize()}: {m:02d}:{s:02d}"
            txt = self.font_small.render(lbl, True, (255,255,255))
            screen.blit(txt, (self.x_offset + 10, 50 + i*30))

        # draw buttons
        for label, rect in self.buttons.items():
            bg = (100, 100, 100)

            # mode highlighting
            if label == "Mode: 1v1" and game.mode == "1v1":
                bg = (100, 200, 100)
            elif label == "Mode: vs AI" and game.mode == "ai":
                bg = (100, 200, 100)

            # difficulty highlighting (only when in AI mode)
            elif label == "Easy":
                if game.mode == "ai":
                    bg = (100, 200, 100) if game.ai.difficulty_level == 1 else (150, 150, 150)
                else:
                    bg = (150, 150, 150)
            elif label == "Medium":
                if game.mode == "ai":
                    bg = (100, 200, 100) if game.ai.difficulty_level == 2 else (150, 150, 150)
                else:
                    bg = (150, 150, 150)
            elif label == "Hard":
                if game.mode == "ai":
                    bg = (100, 200, 100) if game.ai.difficulty_level == 3 else (150, 150, 150)
                else:
                    bg = (150, 150, 150)

            # pause highlighting
            elif label == "Pause" and game.paused:
                bg = (200, 200, 100)

            pygame.draw.rect(screen, bg, rect)
            txt = self.font_small.render(label, True, (0, 0, 0))
            screen.blit(txt, txt.get_rect(center=rect.center))

    def handle_event(self, event, game):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return False
        x, y = event.pos
        if x < self.x_offset:
            return False

        for label, rect in self.buttons.items():
            if not rect.collidepoint(x, y):
                continue

            if label == "Quit":
                pygame.event.post(pygame.event.Event(pygame.QUIT))

            elif label == "Restart":
                game.start_game()

            elif label == "Pause":
                game.paused = not game.paused

            elif label == "Mode: 1v1":
                game.mode = "1v1"
                game.start_game()

            elif label == "Mode: vs AI":
                game.mode = "ai"
                game.start_game()

            elif label == "Easy":
                game.ai.difficulty_level = 1
                game.start_game()

            elif label == "Medium":
                game.ai.difficulty_level = 2
                game.start_game()

            elif label == "Hard":
                game.ai.difficulty_level = 3
                game.start_game()

            return True

        return False
