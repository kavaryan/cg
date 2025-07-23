from utils.judge import Judge

class DebateMatch:
    """Handles individual debate matches"""
    
    @staticmethod
    def play(motion, pro_bot, con_bot):
        log = []
        try:
            for turn in range(3):
                # Pro's turn
                pro_response = pro_bot(log, turn)
                log.append(f"A: {pro_response}")

                # Con's turn
                con_response = con_bot(log, turn)
                log.append(f"B: {con_response}")

            verdict = Judge.judge("\n".join(log))
            return verdict, log
        except Exception as e:
            print(f"Debate error: {e}")
            return {"winner":"draw","score_A":5,"score_B":5,"reason":"error"}, log