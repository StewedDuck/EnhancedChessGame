class AI_Player:
    def __init__(self, difficulty_level):
        self.difficulty_level = difficulty_level
        self.evaluation_score = 0
        self.ai_decision_time = 0

    def compute_move(self, board):
        return None

    def evaluate_board(self, board):
        return 0
