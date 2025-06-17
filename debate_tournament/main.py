import random
import nest_asyncio
from config.settings import setup_environment, MCTS_ITERATIONS, EXPLORATION_CONSTANT, MAX_ROLLOUT_DEPTH
from tournament.tournament_runner import TournamentRunner

def main():
    # Setup
    nest_asyncio.apply()
    random.seed(42)
    setup_environment()
    
    # Run tournament
    tournament = TournamentRunner()
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