from debaters.base_debater import BaseDebater
from mcts.algorithm import MCTSAlgorithm

class TrueMCTSDebater(BaseDebater):
    """True MCTS algorithm debater implementation"""
    
    def __init__(self, side: str, motion: str, iterations: int = None):
        super().__init__(side, motion)
        from config.settings import MCTS_ITERATIONS
        iters = iterations if iterations is not None else MCTS_ITERATIONS
        self.mcts_algorithm = MCTSAlgorithm(side, motion, iterations=iters)
    
    def __call__(self, hist, turn):
        try:
            return self.mcts_algorithm.search(hist)
        except Exception as e:
            print(f"True MCTS error: {e}")
            return "I maintain my position on this important issue."
