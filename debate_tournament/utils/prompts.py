def debater_prompt(side, motion, history=None):
    stance = "FOR" if side=="pro" else "AGAINST"
    context = ""
    if history and len(history) > 0:
        context = f"\nDebate so far:\n" + "\n".join(history[-4:])

    return [
        {"role":"system", "content":
         f"You are a persuasive debater arguing {stance}:\n\"{motion}\"{context}"},
        {"role":"user",   "content":
         "Write ONE compelling sentence (≤25 words) that advances your argument."}
    ]

def scorer_prompt(sentence, side, motion, context=""):
    stance = "FOR" if side=="pro" else "AGAINST"
    return [
        {"role":"system", "content":"Rate persuasiveness 0-10; answer with one integer."},
        {"role":"user", "content":
         f"Motion: {motion}\nContext: {context}\nSentence: {sentence}\nRate for {stance} side."}
    ]