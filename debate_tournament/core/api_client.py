import asyncio
import litellm
from config.settings import API_KEY, MODEL_NAME

class APIClient:
    def __init__(self):
        # Set the API key for litellm
        litellm.api_key = API_KEY
    
    async def gchat(self, messages, temp=0.8, max_tok=256):
        try:
            rsp = await litellm.acompletion(
                model=f"groq/{MODEL_NAME}",
                messages=messages,
                temperature=temp,
                max_tokens=max_tok,
            )
            return rsp.choices[0].message.content.strip()
        except Exception as e:
            print(f"API Error: {e}")
            return "I maintain my position on this important issue."
    
    def run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

# Global instance
api_client = APIClient()
