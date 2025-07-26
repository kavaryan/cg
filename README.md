# Conversation Games
**Code for the paper**:  
📄 _Conversation Games and a Strategic View of the Turing Test_  
by [Kaveh Aryan](mailto:kaveh.aryan@kcl.ac.uk) and [Mudit Jain](mudit.jain2303@gmail.com)

Original paper: 📚 [arXiv:2501.18455](https://arxiv.org/abs/2501.18455),
Latest version: 📚 [View on GitHub](https://github.com/kavaryan/cg/blob/master/paper/2501.18455.pdf) 

⚠️ **This is a work in progress. Expect changes and incomplete features.**

## Debate Tournament
This code implements a framework for running AI debate tournaments, as described in the paper. Different types of debaters—ranging from simple heuristics to advanced Monte Carlo Tree Search (MCTS) agents—compete over debate motions. The goal is to simulate and study strategic conversation behavior in adversarial settings.

### Installation
Ensure you have Python installed (recommended Python 3.7+). Install the required dependencies using:

```bash
pip install -r requirements.txt
```

### Usage

Run the tournament using the main script with configurable parameters:

```bash
python main.py [--debate-prompt-file FILE] [--debater1-type TYPE] [--debater1-max-depth N] [--debater2-type TYPE] [--debater2-max-depth N] [--output FILE]
```

### Arguments

- `--debate-prompt-file`: Path to a debate prompt file (optional).
- `--debater1-type`: Type of debater 1. Choices: `baseline`, `prompt-mcts`, `true-mcts`. Default: `true-mcts`.
- `--debater1-max-depth`: Max depth or iterations for debater 1 (optional).
- `--debater2-type`: Type of debater 2. Choices: `baseline`, `prompt-mcts`, `true-mcts`. Default: `baseline`.
- `--debater2-max-depth`: Max depth or iterations for debater 2 (optional).
- `--output`: Output file to store tournament results (optional).

### Main Components

##### TournamentRunner

Manages and runs the debate tournament. It creates debaters based on specified types, runs multiple matches for each motion, collects results, and prints win-rate summaries.

##### Debaters

- **BaselineDebater**: A simple baseline debater.
- **PromptMCTSDebater**: Uses prompt-based Monte Carlo Tree Search.
- **TrueMCTSDebater**: Uses a true MCTS algorithm for debating, leveraging the `MCTSAlgorithm` class.

##### MCTS Algorithm

The Monte Carlo Tree Search (MCTS) algorithm is used by some debaters to simulate and evaluate debate moves, improving decision-making during debates.

### Example

Run a tournament with a true MCTS debater against a baseline debater:

```bash
python main.py --debater1-type true-mcts --debater2-type baseline --output results.txt
```

### Output

The tournament prints win-rate summaries for each motion and debater pairing. If an output file is specified, results are saved there.

Additionally, a sample debate is run and displayed after the tournament.

### Configuration

MCTS parameters such as iterations, exploration constant, and rollout depth are printed at runtime for reference.

## License

See the LICENSE file for details.

