import re
import json
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
            return {"winner":"A","score_A":7,"score_B":6,"reason":"mock dry-run judgment"}
            
        msgs=[{"role":"system","content":JUDGE_SYS},
              {"role":"user","content":text}]
        for _ in range(2):
            try:
                raw = await api_client.gchat(msgs, temp=0, max_tok=96)
                m = re.search(r"\{.*\}", raw, re.S)
                if m:
                    try:
                        return json.loads(m.group())
                    except:
                        pass
                msgs += [{"role":"assistant","content":raw},
                         {"role":"user","content":"Please correct to valid JSON only."}]
            except:
                continue
        return {"winner":"draw","score_A":5,"score_B":5,"reason":"parse_fail"}
    
    @staticmethod
    def judge(text):
        return api_client.run(Judge.judge_async(text))
