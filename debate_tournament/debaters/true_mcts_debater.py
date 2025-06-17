from debaters.base_debater import BaseDebater
from mcts.algorithm import MCTSAlgorithm

class TrueMCTSDebater(BaseDebater):
    """True MCTS algorithm debater implementation"""
    
    def __init__(self, side: str, motion: str):
        super().__init__(side, motion)
        self.mcts_algorithm = MCTSAlgorithm(side, motion)
    
    def __call__(self, hist, turn):
        try:
            return self.mcts_algorithm.search(hist)
        except Exception as e:
            print(f"True MCTS error: {e}")
            return "I maintain my position on this important issue."