from abc import ABC, abstractmethod

class BaseDebater(ABC):
    """Abstract base class for all debater types"""
    
    def __init__(self, side: str, motion: str):
        self.side = side
        self.motion = motion
    
    @abstractmethod
    def __call__(self, hist, turn):
        """Generate a debate response given history and turn number"""
        pass