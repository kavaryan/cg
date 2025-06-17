import time
from tqdm import tqdm
from debaters.baseline_debater import BaselineDebater
from debaters.prompt_mcts_debater import PromptMCTSDebater
from debaters.true_mcts_debater import TrueMCTSDebater
from tournament.match import DebateMatch
from config.settings import MOTIONS, NUM_MATCHES, SLEEP_SEC

class TournamentRunner:
    """Manages and runs the debate tournament"""
    
    def __init__(self):
        self.results = []
    
    def create_debater_pairs(self, motion):
        """Create all debater combinations for a motion"""
        base_pro, base_con = BaselineDebater("pro", motion), BaselineDebater("con", motion)
        prompt_mcts_pro, prompt_mcts_con = PromptMCTSDebater("pro", motion), PromptMCTSDebater("con", motion)
        true_mcts_pro, true_mcts_con = TrueMCTSDebater("pro", motion), TrueMCTSDebater("con", motion)

        return [
            ("BASELINE vs BASELINE",     base_pro,        base_con),
            ("PROMPT-MCTS vs BASELINE",  prompt_mcts_pro, base_con),
            ("TRUE-MCTS vs BASELINE",    true_mcts_pro,   base_con),
            ("BASELINE vs PROMPT-MCTS",  base_pro,        prompt_mcts_con),
            ("BASELINE vs TRUE-MCTS",    base_pro,        true_mcts_con),
            ("TRUE-MCTS vs PROMPT-MCTS", true_mcts_pro,   prompt_mcts_con),
        ]
    
    def run_tournament(self):
        """Execute the full tournament"""
        for motion in MOTIONS:
            pairs = self.create_debater_pairs(motion)
            
            for label, pro_debater, con_debater in pairs:
                wins = 0
                print(f"{motion[:38]}… | {label} | {NUM_MATCHES} debates")
                
                for i in tqdm(range(NUM_MATCHES), leave=False):
                    try:
                        verdict, _ = DebateMatch.play(motion, pro_debater, con_debater)
                        wins += (verdict["winner"] == "A")
                        time.sleep(SLEEP_SEC)
                    except Exception as e:
                        print(f"Match {i} error: {e}")
                        continue
                
                self.results.append((motion[:38] + "…" * (len(motion) > 38), label, wins / NUM_MATCHES))
    
    def print_results(self):
        """Display tournament results"""
        print("\n===== Win-rate summary =====")
        for motion, label, win_rate in self.results:
            print(f"{motion:<40s} {label:<25s} {win_rate:5.1%}")
    
    def run_sample_debate(self):
        """Run and display a sample debate"""
        print("\nSample debate – TRUE-MCTS vs BASELINE\n" + "-" * 60)
        try:
            true_mcts_debater = TrueMCTSDebater("pro", MOTIONS[0])
            baseline_debater = BaselineDebater("con", MOTIONS[0])
            verdict, sample_log = DebateMatch.play(MOTIONS[0], true_mcts_debater, baseline_debater)
            print("\n".join(sample_log))
            print("\nJudge:", verdict)
        except Exception as e:
            print(f"Sample debate error: {e}")