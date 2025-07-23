import os

# API Configuration
API_KEY = "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"
MODEL_NAME = "gemma2-9b-it"

# Tournament Parameters
MOTIONS = [
    "Governments should ban fossil-fuel cars by 2035.",
    "Universal basic income should replace all means-tested welfare.",
]
NUM_MATCHES = 6
SEARCH_K = 3
SLEEP_SEC = 2

# MCTS Algorithm Parameters
MCTS_ITERATIONS = 20
EXPLORATION_CONSTANT = 1.414
MAX_ROLLOUT_DEPTH = 4
MCTS_TEMP = 1.0

# Environment Setup
def setup_environment():
    if not API_KEY or API_KEY == "paste_your_groq_api_key_here":
        raise ValueError("❌  Replace API_KEY with your actual Groq key.")
    os.environ["GROQ_API_KEY"] = API_KEY