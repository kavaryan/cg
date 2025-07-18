import time
from tqdm import tqdm
from debaters.baseline_debater import BaselineDebater
from debaters.prompt_mcts_debater import PromptMCTSDebater
from debaters.true_mcts_debater import TrueMCTSDebater
from tournament.match import DebateMatch
from config.settings import MOTIONS, NUM_MATCHES, SLEEP_SEC

class TournamentRunner:
    """Manages and runs the debate tournament"""

    def __init__(self, debater1_type="true-mcts", debater1_max_depth=None,
                 debater2_type="baseline", debater2_max_depth=None,
                 debate_prompt_file=None, output_file=None):
        self.results = []
        self.debater1_type = debater1_type
        self.debater1_max_depth = debater1_max_depth
        self.debater2_type = debater2_type
        self.debater2_max_depth = debater2_max_depth
        self.debate_prompt_file = debate_prompt_file
        self.output_file = output_file
        self.output_lines = []

    def create_debater(self, debater_type, side, motion, max_depth):
        if debater_type == "baseline":
            from debaters.baseline_debater import BaselineDebater
            return BaselineDebater(side, motion)
        elif debater_type == "prompt-mcts":
            from debaters.prompt_mcts_debater import PromptMCTSDebater
            k = max_depth if max_depth is not None else None
            return PromptMCTSDebater(side, motion, k=k)
        elif debater_type == "true-mcts":
            from debaters.true_mcts_debater import TrueMCTSDebater
            # Pass max_depth as iterations to MCTSAlgorithm inside TrueMCTSDebater
            # We will modify TrueMCTSDebater to accept iterations param
            return TrueMCTSDebater(side, motion, iterations=max_depth)
        else:
            raise ValueError(f"Unknown debater type: {debater_type}")

    def create_debater_pairs(self, motion):
        """Create all debater combinations for a motion"""
        base_pro = self.create_debater(self.debater1_type, "pro", motion, self.debater1_max_depth)
        base_con = self.create_debater(self.debater2_type, "con", motion, self.debater2_max_depth)

        return [
            (f"{self.debater1_type.upper()} vs {self.debater2_type.upper()}", base_pro, base_con),
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
                self.output_lines.append(f"{motion[:38]}… | {label} | {wins / NUM_MATCHES:.2%}")

        if self.output_file:
            with open(self.output_file, "w") as f:
                f.write("\n".join(self.output_lines))

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
