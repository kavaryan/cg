import re
from core.api_client import api_client
from utils.prompts import scorer_prompt

def score_sentence(sent, side, motion, context=""):
    try:
        out = api_client.run(api_client.gchat(scorer_prompt(sent, side, motion, context), temp=0, max_tok=8))
        m = re.search(r"\d+", out)
        return int(m.group()) if m else 5
    except:
        return 5