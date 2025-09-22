import re
import json
import random
from core.api_client import api_client

JUDGE_SYS = (
 "You are the sole judge of a three-round debate.\n"
 'Return JSON: {"winner":"A|B|draw","score_A":0-10,"score_B":0-10,"reason":"<20 words>"}'
)

class Judge:
    @staticmethod
    async def judge_async(text):
        # Return mock judgment in dry-run mode
        if api_client.dry_run:
            winner = random.choice(["A", "B", "draw"])
            score_a = random.randint(3, 10)
            score_b = random.randint(3, 10)
            return {"winner":winner,"score_A":score_a,"score_B":score_b,"reason":"mock dry-run judgment"}

        msgs=[{"role":"system","content":JUDGE_SYS},
              {"role":"user","content":text}]

        # Try multiple parsing strategies
        for attempt in range(3):
            try:
                raw = await api_client.gchat(msgs, temp=0, max_tok=96, call_type='judge')

                # Strategy 1: Try to find JSON in the response
                json_match = re.search(r'\{.*\}', raw, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                        # Validate required fields
                        if all(key in result for key in ["winner", "score_A", "score_B", "reason"]):
                            return result
                    except json.JSONDecodeError:
                        pass

                # Strategy 2: If first attempt failed, ask for correction
                if attempt < 2:
                    msgs += [{"role":"assistant","content":raw},
                             {"role":"user","content":"Please respond with valid JSON only: {\"winner\":\"A|B|draw\",\"score_A\":0-10,\"score_B\":0-10,\"reason\":\"<20 words>\"}"}]

            except Exception as e:
                if attempt == 2:  # Last attempt
                    print(f"Judge parsing error: {e}")
                continue

        # Final fallback
        return {"winner":"draw","score_A":5,"score_B":5,"reason":"parse_fail"}

    @staticmethod
    def judge(text):
        if api_client.dry_run:
            winner = random.choice(["A", "B", "draw"])
            score_a = random.randint(3, 10)
            score_b = random.randint(3, 10)
            return {"winner":winner,"score_A":score_a,"score_B":score_b,"reason":"mock dry-run judgment"}
        return api_client.run(Judge.judge_async(text))
