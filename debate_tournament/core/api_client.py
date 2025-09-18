import asyncio
import os
import traceback
import litellm

class APIClient:
    def __init__(self, api_key: str, model_name: str, dry_run: bool = False):
        # Set the API key for litellm only if not in dry-run mode
        if not dry_run:
            litellm.api_key = api_key
        self.model_name = model_name
        self.dry_run = dry_run
        self._mock_responses = [
            "I believe this argument has strong merit.",
            "The evidence clearly supports this position.",
            "This perspective overlooks key considerations.",
            "The data demonstrates significant benefits.",
            "There are important counterarguments to consider.",
            "This approach offers the most practical solution.",
            "The research indicates substantial risks.",
            "This viewpoint fails to address core issues."
        ]
        self._response_counter = 0

    async def gchat(self, messages, temp=0.8, max_tok=256):
        if self.dry_run:
            # Return mock response for dry-run mode
            response = self._mock_responses[self._response_counter % len(self._mock_responses)]
            self._response_counter += 1
            return response
            
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
            print("Full traceback:")
            traceback.print_exc()
            return "I maintain my position on this important issue."
    
    def run(self, coro):
        if self.dry_run:
            # In dry-run mode, we need to run the coroutine to get the mock result
            # but we can do it synchronously since it's just returning a mock value
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(coro)
                return result
            finally:
                loop.close()
        else:
            return asyncio.get_event_loop().run_until_complete(coro)

# Global instance - will be reconfigured in main based on dry_run flag
api_client = APIClient(os.environ.get("GROQ_API_KEY"), "qwen/qwen3-32b")

def configure_api_client(dry_run: bool = False):
    """Reconfigure the global API client for dry-run mode"""
    global api_client
    api_client = APIClient(os.environ.get("GROQ_API_KEY"), "qwen/qwen3-32b", dry_run=dry_run)
