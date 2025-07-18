import random
import nest_asyncio
import argparse
from config.settings import setup_environment, MCTS_ITERATIONS, EXPLORATION_CONSTANT, MAX_ROLLOUT_DEPTH
from tournament.tournament_runner import TournamentRunner

def main():
    parser = argparse.ArgumentParser(description="Run debate tournament with configurable parameters.")
    parser.add_argument("--debate-prompt-file", type=str, default=None, help="Path to debate prompt file")
    parser.add_argument("--debater1-type", type=str, choices=["baseline", "prompt-mcts", "true-mcts"], default="true-mcts", help="Type of debater 1")
    parser.add_argument("--debater1-max-depth", type=int, default=None, help="Max depth or iterations for debater 1")
    parser.add_argument("--debater2-type", type=str, choices=["baseline", "prompt-mcts", "true-mcts"], default="baseline", help="Type of debater 2")
    parser.add_argument("--debater2-max-depth", type=int, default=None, help="Max depth or iterations for debater 2")
    parser.add_argument("--output", type=str, default=None, help="Output file to store results")
    args = parser.parse_args()

    # Setup
    nest_asyncio.apply()
    random.seed(42)
    setup_environment()

    # Run tournament with passed arguments
    tournament = TournamentRunner(
        debater1_type=args.debater1_type,
        debater1_max_depth=args.debater1_max_depth,
        debater2_type=args.debater2_type,
        debater2_max_depth=args.debater2_max_depth,
        debate_prompt_file=args.debate_prompt_file,
        output_file=args.output
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
