import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class MCTSNode:
    """Node in the MCTS tree representing a game state"""
    state: List[str]
    side: str        # Which side is to move ('pro' or 'con')
    motion: str      # The debate motion
    parent: Optional['MCTSNode'] = None
    children: Dict[str, 'MCTSNode'] = field(default_factory=dict)
    visits: int = 0
    total_reward: float = 0.0
    untried_actions: List[str] = field(default_factory=list)
    is_terminal: bool = False

    @property
    def value(self) -> float:
        """Average reward for this node"""
        return self.total_reward / self.visits if self.visits > 0 else 0.0

    def is_fully_expanded(self) -> bool:
        """Check if all possible actions have been tried"""
        # If we haven't generated actions yet, we're not fully expanded
        if not self.children and not self.untried_actions:
            return False
        # If we have untried actions, we're not fully expanded
        return len(self.untried_actions) == 0

    def best_child(self, exploration_weight: float) -> Optional['MCTSNode']:
        """Select best child using UCB1 formula"""
        if not self.children:
            return None

        def ucb1_score(child):
            if child.visits == 0:
                return float('inf')

            exploitation = child.total_reward / child.visits
            if self.visits <= 0:
                return exploitation
            exploration = exploration_weight * math.sqrt(math.log(self.visits) / child.visits)
            return exploitation + exploration

        try:
            return max(self.children.values(), key=ucb1_score)
        except (ValueError, ZeroDivisionError):
            return list(self.children.values())[0] if self.children else None

    def update(self, reward: float):
        """Update this node's statistics"""
        self.visits += 1
        self.total_reward += reward

    def add_child(self, action: str, child_state: List[str], child_side: str) -> 'MCTSNode':
        """Add a new child node"""
        child = MCTSNode(
            state=child_state,
            side=child_side,
            motion=self.motion,
            parent=self
        )
        self.children[action] = child
        # Don't remove from untried_actions here since expand() already did it
        return child
