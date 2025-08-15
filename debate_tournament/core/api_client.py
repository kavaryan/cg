import asyncio
import litellm

class APIClient:
    def __init__(self, api_key: str, model_name: str):
        # Set the API key for litellm
        litellm.api_key = api_key
        self.model_name = model_name

    async def gchat(self, messages, temp=0.8, max_tok=256):
        try:
            rsp = await litellm.acompletion(
                model=f"groq/{self.model_name}",
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
