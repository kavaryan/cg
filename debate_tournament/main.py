import random

try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    print("nest_asyncio is not installed. Some async operations may not work as expected.")
    pass

import argparse
from tournament.tournament_runner import TournamentRunner

MCTS_ITERATIONS = 20
EXPLORATION_CONSTANT = 1.414
MAX_ROLLOUT_DEPTH = 4
MCTS_TEMP = 1.0

def main():
    parser = argparse.ArgumentParser(description="Run debate tournament with configurable parameters.")
    parser.add_argument("--debate-prompt-file", type=str, default=None, help="Path to debate prompt file")
    parser.add_argument("--debater1-type", type=str, choices=["baseline", "prompt-mcts", "true-mcts"], default="true-mcts", help="Type of debater 1")
    parser.add_argument("--debater1-iterations", type=int, default=None, help="Number of MCTS iterations for debater 1")
    parser.add_argument("--debater2-type", type=str, choices=["baseline", "prompt-mcts", "true-mcts"], default="baseline", help="Type of debater 2")
    parser.add_argument("--debater2-iterations", type=int, default=None, help="Number of MCTS iterations for debater 2")
    parser.add_argument("--max-debate-depth", type=int, default=6, help="Maximum number of moves in a debate")
    parser.add_argument("--output", type=str, default=None, help="Output file to store results")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode with MCTS tree visualization (no LLM calls)")
    args = parser.parse_args()

    # Setup
    
    random.seed(42)
    # setup_environment()
    
    # Define debate motions
    motions = [
        "This house believes that artificial intelligence will do more harm than good",
        "This house believes that social media has a net negative impact on society",
        "This house believes that remote work is better than office work",
        "This house believes that nuclear energy is the best solution to climate change"
    ]

    # Run tournament with passed arguments
    tournament = TournamentRunner(
        motions,
        debater1_type=args.debater1_type,
        debater1_iterations=args.debater1_iterations,
        debater2_type=args.debater2_type,
        debater2_iterations=args.debater2_iterations,
        max_debate_depth=args.max_debate_depth,
        debate_prompt_file=args.debate_prompt_file,
        output_file=args.output,
        dry_run=args.dry_run
    )
    tournament.run_tournament()
    tournament.print_results()
    tournament.run_sample_debate()

    # Print MCTS configuration
    print(f"\n===== MCTS Configuration =====")
    print(f"MCTS Iterations per move: {MCTS_ITERATIONS}")
    print(f"Exploration Constant (C): {EXPLORATION_CONSTANT}")
    print(f"Max Rollout Depth: {MAX_ROLLOUT_DEPTH}")
    print(f"Candidate Actions per Node: 3")
    print(f"Total API calls per TRUE-MCTS move: ~{MCTS_ITERATIONS + 15} (search + evaluation)")

if __name__ == "__main__":
    main()
