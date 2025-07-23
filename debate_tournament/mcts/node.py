import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from config.settings import EXPLORATION_CONSTANT

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

    def is_fully_expanded(self) -> bool:
        """Check if all possible actions have been tried"""
        if not self.children and not self.untried_actions:
            return False
        return len(self.untried_actions) == 0

    def best_child(self, exploration_weight: float = EXPLORATION_CONSTANT) -> Optional['MCTSNode']:
        """Select best child using UCB1 formula"""
        if not self.children:
            return None

        def ucb1_score(child):
            if child.visits == 0:
                return float('inf')

            exploitation = child.total_reward / child.visits
            exploration = exploration_weight * math.sqrt(math.log(self.visits) / child.visits)
            return exploitation + exploration

        return max(self.children.values(), key=ucb1_score)

    def update(self, reward: float):
        """Backpropagate reward up the tree"""
        self.visits += 1
        self.total_reward += reward
        if self.parent:
            self.parent.update(-reward)

    def add_child(self, action: str, child_state: List[str], child_side: str) -> 'MCTSNode':
        """Add a new child node"""
        child = MCTSNode(
            state=child_state,
            side=child_side,
            motion=self.motion,
            parent=self
        )
        self.children[action] = child
        if action in self.untried_actions:
            self.untried_actions.remove(action)
        return child