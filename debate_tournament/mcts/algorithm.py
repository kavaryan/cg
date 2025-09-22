import re
import math
import random
from typing import List, Optional
from mcts.node import MCTSNode
from utils.prompts import debater_prompt
from utils.scoring import score_sentence
from core.api_client import api_client

EXPLORATION_CONSTANT = 1.414


class MCTSAlgorithm:
    """True MCTS algorithm implementation for debate"""

    def __init__(self, side: str, motion: str,
            iterations: int, max_rollout_depth: int, max_debate_depth: int, exploration_constant: Optional[float] = None, dry_run: bool = False):
        self.side = side
        self.motion = motion
        self.iterations = iterations
        self.max_rollout_depth = max_rollout_depth
        self.max_debate_depth = max_debate_depth  # Now properly used
        self.exploration_constant = exploration_constant if exploration_constant is not None else EXPLORATION_CONSTANT
        self.dry_run = dry_run
        self.tree_log = []

    def generate_candidate_actions(self, state: List[str], num_candidates: int = 3) -> List[str]:
        """Generate candidate debate responses"""
        if self.dry_run:
            # Return mock candidate actions for dry-run mode
            mock_candidates = [
                f"Mock argument {len(state)+1}.1 for {self.side} side",
                f"Evidence-based point {len(state)+1}.2 supporting our position",
                f"Counter-argument {len(state)+1}.3 addressing opposition concerns"
            ]
            return mock_candidates[:num_candidates]

        candidates = []
        max_attempts = num_candidates * 5  # Increased attempts to prevent infinite loops
        attempts = 0

        while len(candidates) < num_candidates and attempts < max_attempts:
            try:
                response = api_client.run(api_client.gchat(
                    debater_prompt(self.side, self.motion, state),
                    temp=1.2,
                    max_tok=40
                ))
                if response and response.strip() not in candidates and len(response.strip()) > 0:
                    candidates.append(response.strip())
                attempts += 1
            except Exception as e:
                attempts += 1
                if not self.dry_run:
                    print(f"Error generating candidate {attempts}: {e}")
                continue

        # Fallback if no candidates generated
        while len(candidates) < num_candidates:
            candidates.append(f"I maintain my position on this important issue (attempt {len(candidates)+1})")

        return candidates

    def evaluate_state(self, state: List[str]) -> float:
        """Evaluate the current debate state from this side's perspective"""
        if len(state) == 0:
            return 0.0

        if self.dry_run:
            # Return mock evaluation for dry-run mode
            return random.uniform(-0.5, 0.5)

        try:
            if len(state) > 0:
                last_statement = state[-1]
                clean_statement = re.sub(r'^[AB]: ', '', last_statement)

                # Determine which side made the last statement
                last_index = len(state) - 1
                last_side = "pro" if last_index % 2 == 0 else "con"

                # Evaluate based on whether it's our statement or opponent's
                if last_side == self.side:
                    # Our statement - positive evaluation
                    context = "\n".join(state[-4:]) if len(state) > 4 else "\n".join(state)
                    score = score_sentence(clean_statement, self.side, self.motion, context)
                    return max(-1.0, min(1.0, (score - 5.0) / 5.0))  # Clamp to [-1, 1]
                else:
                    # Opponent's statement - negative evaluation
                    opponent_side = "con" if self.side == "pro" else "pro"
                    context = "\n".join(state[-4:]) if len(state) > 4 else "\n".join(state)
                    score = score_sentence(clean_statement, opponent_side, self.motion, context)
                    return max(-1.0, min(1.0, -(score - 5.0) / 5.0))  # Clamp to [-1, 1]

            return 0.0
        except Exception as e:
            if not self.dry_run:
                print(f"State evaluation error: {e}")
            return 0.0

    def simulate_random_playout(self, state: List[str], current_side: str, depth: int = 0) -> float:
        """Simulate a random playout from the current state"""
        # Use max_rollout_depth for simulation depth, not max_debate_depth
        if depth >= self.max_rollout_depth:
            return self.evaluate_state(state)

        # Check if we've exceeded max debate depth
        if len(state) >= self.max_debate_depth * 2:
            return self.evaluate_state(state)

        try:
            if self.dry_run:
                # Mock response for dry-run mode
                response = f"Mock response for {current_side} at depth {depth}"
            else:
                response = api_client.run(api_client.gchat(
                    debater_prompt(current_side, self.motion, state),
                    temp=1.5,
                    max_tok=40
                ))

            side_letter = "A" if current_side == "pro" else "B"
            new_state = state + [f"{side_letter}: {response}"]
            next_side = "con" if current_side == "pro" else "pro"

            return self.simulate_random_playout(new_state, next_side, depth + 1)
        except Exception as e:
            if not self.dry_run:
                print(f"Simulation error: {e}")
            return self.evaluate_state(state)

    def select(self, node: MCTSNode) -> MCTSNode:
        """Selection phase: traverse tree using UCB1"""
        current = node
        while current is not None and not current.is_terminal and current.is_fully_expanded():
            best_child = current.best_child(self.exploration_constant)
            if best_child is None:
                break
            current = best_child
        return current if current is not None else node

    def expand(self, node: MCTSNode) -> Optional[MCTSNode]:
        """Expansion phase: add new child node"""
        # Check if we've reached max debate depth
        if len(node.state) >= self.max_debate_depth * 2:
            node.is_terminal = True
            return node

        # Prevent infinite expansion during search
        if node.is_terminal or len(node.state) >= 50:
            node.is_terminal = True
            return node

        # Generate actions if we haven't yet
        if not node.children and not node.untried_actions:
            node.untried_actions = self.generate_candidate_actions(node.state)
            if not node.untried_actions:
                node.is_terminal = True
                return node

        # If we have untried actions, expand one
        if node.untried_actions:
            action = node.untried_actions.pop(0)  # Remove the action we're expanding

            side_letter = "A" if node.side == "pro" else "B"
            new_state = node.state + [f"{side_letter}: {action}"]
            next_side = "con" if node.side == "pro" else "pro"

            child = node.add_child(action, new_state, next_side)
            return child

        # If fully expanded, return the node itself
        return node

    def simulate(self, node: MCTSNode) -> float:
        """Simulation phase: random playout"""
        try:
            return self.simulate_random_playout(node.state, node.side)
        except Exception as e:
            if not self.dry_run:
                print(f"Simulation error: {e}")
            return 0.0

    def backpropagate(self, node: MCTSNode, reward: float):
        """Backpropagation phase: update node values"""
        current = node
        multiplier = 1.0
        while current is not None:
            current.update(reward * multiplier)
            current = current.parent
            multiplier *= -1  # Alternate reward for opponent

    def print_tree_structure(self, node: MCTSNode, prefix: str = "", is_last: bool = True, depth: int = 0):
        """Print the MCTS tree structure with numbered nodes"""
        if depth > 15:  # Show even deeper trees to see the full exploration
            return

        # Create the tree visualization
        connector = "└── " if is_last else "├── "
        node_info = f"visits={node.visits}, value={node.value:.3f}"

        if hasattr(node, 'action') and node.action:
            action_preview = node.action[:30] + "..." if len(node.action) > 30 else node.action
            print(f"{prefix}{connector}[{node_info}] \"{action_preview}\"")
        else:
            print(f"{prefix}{connector}[ROOT] {node_info}")

        # Prepare prefix for children
        child_prefix = prefix + ("    " if is_last else "│   ")

        # Print children
        children_list = list(node.children.items())
        for i, (action, child) in enumerate(children_list):
            child.action = action  # Store action for display
            is_last_child = (i == len(children_list) - 1)
            self.print_tree_structure(child, child_prefix, is_last_child, depth + 1)

    def search(self, root_state: List[str]) -> str:
        """Main MCTS search algorithm"""
        if self.dry_run:
            print(f"\n=== DRY-RUN MCTS SEARCH ({self.side.upper()}) ===")
            print(f"Motion: {self.motion}")
            print(f"Current state: {len(root_state)} moves")
            print(f"Iterations: {self.iterations}")
            print(f"Max rollout depth: {self.max_rollout_depth}")
            print(f"Max debate depth: {self.max_debate_depth}")
            print(f"Exploration constant: {self.exploration_constant}")
            print("-" * 50)

        try:
            root = MCTSNode(
                state=root_state,
                side=self.side,
                motion=self.motion
            )

            for iteration in range(self.iterations):
                try:
                    if self.dry_run:
                        print(f"\nIteration {iteration + 1}:")

                    leaf = self.select(root)
                    if leaf is None:
                        leaf = root

                    if not leaf.is_terminal:
                        expanded_leaf = self.expand(leaf)
                        if expanded_leaf is not None:
                            leaf = expanded_leaf
                        if self.dry_run:
                            if expanded_leaf != leaf:
                                print(f"  Expanded new child node (parent now has {len(leaf.children)} children)")
                            else:
                                print(f"  Node already fully expanded ({len(leaf.children)} children)")

                    reward = self.simulate(leaf)
                    if self.dry_run:
                        print(f"  Simulation reward: {reward:.3f} (max depth: {self.max_rollout_depth})")

                    if leaf is not None:
                        self.backpropagate(leaf, reward)

                except Exception as e:
                    if self.dry_run:
                        print(f"  Error in iteration {iteration}: {e}")
                        import traceback
                        traceback.print_exc()
                    else:
                        print(f"MCTS iteration {iteration} error: {e}")
                    continue

            if self.dry_run:
                print(f"\n=== FINAL MCTS TREE ===")
                self.print_tree_structure(root)
                print(f"\n=== TREE STATISTICS ===")
                print(f"Root visits: {root.visits}")
                print(f"Root children: {len(root.children)}")
                if root.children:
                    best_child = max(root.children.values(), key=lambda c: c.visits)
                    print(f"Best child visits: {best_child.visits}")
                    print(f"Best child value: {best_child.value:.3f}")

            if not root.children:
                candidates = self.generate_candidate_actions(root_state, 1)
                result = candidates[0] if candidates else "I maintain my position on this important issue."
                if self.dry_run:
                    print(f"\nSelected action (no children): {result}")
                return result

            best_child = max(root.children.values(), key=lambda c: c.visits)
            for action, child in root.children.items():
                if child == best_child:
                    if self.dry_run:
                        print(f"\nSelected action: {action}")
                    return action

            result = list(root.children.keys())[0]
            if self.dry_run:
                print(f"\nSelected action (fallback): {result}")
            return result

        except Exception as e:
            if self.dry_run:
                print(f"MCTS search error: {e}")
                import traceback
                traceback.print_exc()
            else:
                print(f"MCTS search error: {e}")
            try:
                candidates = self.generate_candidate_actions(root_state, 1)
                return candidates[0] if candidates else "I maintain my position on this important issue."
            except Exception:
                return "I maintain my position on this important issue."
