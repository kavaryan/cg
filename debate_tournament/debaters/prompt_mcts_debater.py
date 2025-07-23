from debaters.base_debater import BaseDebater
from utils.prompts import debater_prompt
from utils.scoring import score_sentence
from core.api_client import api_client
from config.settings import SEARCH_K

class PromptMCTSDebater(BaseDebater):
    """Prompt-based MCTS debater implementation"""
    
    def __init__(self, side: str, motion: str, k: int = SEARCH_K):
        super().__init__(side, motion)
        self.k = k
    
    def __call__(self, hist, turn):
        try:
            best, best_s = "", -1
            context = "\n".join(hist[-4:]) if len(hist) > 4 else "\n".join(hist)
            for _ in range(self.k):
                cand = api_client.run(api_client.gchat(debater_prompt(self.side, self.motion, hist), temp=1.2, max_tok=40))
                sc = score_sentence(cand, self.side, self.motion, context)
                if sc > best_s:
                    best_s, best = sc, cand
            return best if best else "I maintain my position on this important issue."
        except:
            return "I maintain my position on this important issue."