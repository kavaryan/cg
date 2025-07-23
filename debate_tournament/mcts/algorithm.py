import re
from typing import List
from mcts.node import MCTSNode
from utils.prompts import debater_prompt
from utils.scoring import score_sentence
from core.api_client import api_client
from config.settings import MCTS_ITERATIONS, MAX_ROLLOUT_DEPTH

class MCTSAlgorithm:
    """True MCTS algorithm implementation for debate"""

    def __init__(self, side: str, motion: str, iterations: int = MCTS_ITERATIONS):
        self.side = side
        self.motion = motion
        self.iterations = iterations

    def generate_candidate_actions(self, state: List[str], num_candidates: int = 3) -> List[str]:
        """Generate candidate debate responses"""
        candidates = []
        for attempt in range(num_candidates * 2):
            try:
                response = api_client.run(api_client.gchat(
                    debater_prompt(self.side, self.motion, state),
                    temp=1.2,
                    max_tok=40
                ))
                if response and response not in candidates and len(response.strip()) > 0:
                    candidates.append(response.strip())
                    if len(candidates) >= num_candidates:
                        break
            except Exception as e:
                continue

        if not candidates:
            candidates = ["I maintain my position on this important issue."]

        return candidates

    def evaluate_state(self, state: List[str]) -> float:
        """Evaluate the current debate state from this side's perspective"""
        if len(state) == 0:
            return 0.0

        try:
            if len(state) > 0:
                last_statement = state[-1]
                clean_statement = re.sub(r'^[AB]: ', '', last_statement)

                last_index = len(state) - 1
                is_our_statement = (last_index % 2 == 0 and self.side == "pro") or (last_index % 2 == 1 and self.side == "con")

                if is_our_statement:
                    context = "\n".join(state[-4:]) if len(state) > 4 else "\n".join(state)
                    score = score_sentence(clean_statement, self.side, self.motion, context)
                    return (score - 5.0) / 5.0
                else:
                    opponent_side = "con" if self.side == "pro" else "pro"
                    context = "\n".join(state[-4:]) if len(state) > 4 else "\n".join(state)
                    score = score_sentence(clean_statement, opponent_side, self.motion, context)
                    return -(score - 5.0) / 5.0

            return 0.0
        except:
            return 0.0

    def simulate_random_playout(self, state: List[str], current_side: str, depth: int = 0) -> float:
        """Simulate a random playout from the current state"""
        if depth >= MAX_ROLLOUT_DEPTH or len(state) >= 6:
            return self.evaluate_state(state)

        try:
            response = api_client.run(api_client.gchat(
                debater_prompt(current_side, self.motion, state),
                temp=1.5,
                max_tok=40
            ))

            side_letter = "A" if current_side == "pro" else "B"
            new_state = state + [f"{side_letter}: {response}"]
            next_side = "con" if current_side == "pro" else "pro"

            return self.simulate_random_playout(new_state, next_side, depth + 1)
        except:
            return self.evaluate_state(state)

    def select(self, node: MCTSNode) -> MCTSNode:
        """Selection phase: traverse tree using UCB1"""
        current = node
        while current is not None and not current.is_terminal and current.is_fully_expanded():
            best_child = current.best_child()
            if best_child is None:
                break
            current = best_child
        return current if current is not None else node

    def expand(self, node: MCTSNode) -> MCTSNode:
        """Expansion phase: add new child node"""
        if node.is_terminal or len(node.state) >= 6:
            node.is_terminal = True
            return node

        if not node.children and not node.untried_actions:
            node.untried_actions = self.generate_candidate_actions(node.state)
            if not node.untried_actions:
                node.is_terminal = True
                return node

        if node.untried_actions:
            action = node.untried_actions[0]

            side_letter = "A" if node.side == "pro" else "B"
            new_state = node.state + [f"{side_letter}: {action}"]
            next_side = "con" if node.side == "pro" else "pro"

            child = node.add_child(action, new_state, next_side)
            return child

        return node

    def simulate(self, node: MCTSNode) -> float:
        """Simulation phase: random playout"""
        try:
            return self.simulate_random_playout(node.state, node.side)
        except:
            return 0.0

    def backpropagate(self, node: MCTSNode, reward: float):
        """Backpropagation phase: update node values"""
        node.update(reward)

    def search(self, root_state: List[str]) -> str:
        """Main MCTS search algorithm"""
        try:
            root = MCTSNode(
                state=root_state,
                side=self.side,
                motion=self.motion
            )

            for iteration in range(self.iterations):
                try:
                    leaf = self.select(root)
                    if leaf is None:
                        leaf = root

                    if not leaf.is_terminal and len(leaf.state) < 6:
                        leaf = self.expand(leaf)

                    reward = self.simulate(leaf)
                    self.backpropagate(leaf, reward)

                except Exception as e:
                    print(f"MCTS iteration {iteration} error: {e}")
                    continue

            if not root.children:
                candidates = self.generate_candidate_actions(root_state, 1)
                return candidates[0] if candidates else "I maintain my position on this important issue."

            best_child = max(root.children.values(), key=lambda c: c.visits)
            for action, child in root.children.items():
                if child == best_child:
                    return action

            return list(root.children.keys())[0]

        except Exception as e:
            print(f"MCTS search error: {e}")
            try:
                candidates = self.generate_candidate_actions(root_state, 1)
                return candidates[0] if candidates else "I maintain my position on this important issue."
            except:
                return "I maintain my position on this important issue."