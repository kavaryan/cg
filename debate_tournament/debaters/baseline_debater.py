from debaters.base_debater import BaseDebater
from utils.prompts import debater_prompt
from core.api_client import api_client

class BaselineDebater(BaseDebater):
    """Original baseline debater implementation"""
    
    def __call__(self, hist, turn):
        try:
            return api_client.run(api_client.gchat(debater_prompt(self.side, self.motion, hist), temp=0.9, max_tok=40))
        except:
            return "I maintain my position on this important issue."