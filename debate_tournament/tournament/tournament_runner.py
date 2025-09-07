import time
from tqdm import tqdm
from debaters.baseline_debater import BaselineDebater
from debaters.prompt_mcts_debater import PromptMCTSDebater
from debaters.true_mcts_debater import TrueMCTSDebater
from tournament.match import DebateMatch

class TournamentRunner:
    """Manages and runs the debate tournament"""

    def __init__(self, motions, debater1_type="true-mcts", debater1_iterations=None, debater1_max_rollout_depth=None,
                 debater2_type="baseline", debater2_iterations=None, debater2_max_rollout_depth=None,
                 max_debate_depth=6, debate_prompt_file=None, output_file=None, dry_run=False):
        self.motions = motions
        self.results = []
        self.debater1_type = debater1_type
        self.debater1_iterations = debater1_iterations
        self.debater1_max_rollout_depth = debater1_max_rollout_depth
        self.debater2_type = debater2_type
        self.debater2_iterations = debater2_iterations
        self.debater2_max_rollout_depth = debater2_max_rollout_depth
        self.max_debate_depth = max_debate_depth
        self.debate_prompt_file = debate_prompt_file
        self.output_file = output_file
        self.output_lines = []
        self.dry_run = dry_run
        
        # Configure API client for dry-run mode
        if dry_run:
            from core.api_client import configure_api_client
            configure_api_client(dry_run=True)

    def create_debater(self, debater_type, side, motion, iterations, max_rollout_depth=None):
        if debater_type == "baseline":
            from debaters.baseline_debater import BaselineDebater
            return BaselineDebater(side, motion)
        elif debater_type == "prompt-mcts":
            from debaters.prompt_mcts_debater import PromptMCTSDebater
            k = iterations if iterations is not None else 3
            return PromptMCTSDebater(side, motion, k=k)
        elif debater_type == "true-mcts":
            from debaters.true_mcts_debater import TrueMCTSDebater
            # Pass iterations, max_rollout_depth and max_debate_depth to MCTSAlgorithm inside TrueMCTSDebater
            iterations = iterations if iterations is not None else 20
            max_rollout_depth = max_rollout_depth if max_rollout_depth is not None else 4
            return TrueMCTSDebater(side, motion, iterations=iterations, max_rollout_depth=max_rollout_depth, max_debate_depth=self.max_debate_depth, dry_run=self.dry_run)
        else:
            raise ValueError(f"Unknown debater type: {debater_type}")

    def create_debater_pairs(self, motion):
        """Create all debater combinations for a motion"""
        base_pro = self.create_debater(self.debater1_type, "pro", motion, self.debater1_iterations, self.debater1_max_rollout_depth)
        base_con = self.create_debater(self.debater2_type, "con", motion, self.debater2_iterations, self.debater2_max_rollout_depth)

        return [
            (f"{self.debater1_type.upper()} vs {self.debater2_type.upper()}", base_pro, base_con),
        ]

    def run_tournament(self, num_matches: int = 6, sleep_sec: float = 2.0):
        """Execute the full tournament"""
        if self.dry_run:
            print("=== DRY-RUN MODE: MCTS Tree Visualization ===")
            num_matches = 1  # Only run one match in dry-run mode
            sleep_sec = 0  # No sleep needed in dry-run
            
        for motion in self.motions:
            pairs = self.create_debater_pairs(motion)

            for label, pro_debater, con_debater in pairs:
                wins = 0
                if not self.dry_run:
                    print(f"{motion[:38]}… | {label} | {num_matches} debates")

                for i in tqdm(range(num_matches), leave=False, disable=self.dry_run):
                    try:
                        verdict, _ = DebateMatch.play(motion, pro_debater, con_debater)
                        wins += (verdict["winner"] == "A")
                        if not self.dry_run:
                            time.sleep(sleep_sec)
                    except Exception as e:
                        print(f"Match {i} error: {e}")
                        continue

                if not self.dry_run:
                    self.results.append((motion[:38] + "…" * (len(motion) > 38), label, wins / num_matches))
                    self.output_lines.append(f"{motion[:38]}… | {label} | {wins / num_matches:.2%}")

        if self.output_file and not self.dry_run:
            with open(self.output_file, "w") as f:
                f.write("\n".join(self.output_lines))

    def print_results(self):
        """Display tournament results"""
        print("\n===== Win-rate summary =====")
        for motion, label, win_rate in self.results:
            print(f"{motion:<40s} {label:<25s} {win_rate:5.1%}")

    def run_sample_debate(self):
        """Run and display a sample debate"""
        if self.dry_run:
            print("\n=== DRY-RUN COMPLETE ===")
            print("MCTS tree search visualization shown above.")
            return
            
        print("\nSample debate – TRUE-MCTS vs BASELINE\n" + "-" * 60)
        try:
            true_mcts_debater = TrueMCTSDebater("pro", self.motions[0], max_debate_depth=self.max_debate_depth)
            baseline_debater = BaselineDebater("con", self.motions[0])
            verdict, sample_log = DebateMatch.play(self.motions[0], true_mcts_debater, baseline_debater)
            print("\n".join(sample_log))
            print("\nJudge:", verdict)
        except Exception as e:
            print(f"Sample debate error: {e}")
