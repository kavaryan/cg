import asyncio
import os
import traceback
import litellm

class APIClient:
    def __init__(self, api_key: str, model_name: str, base_url: str = None, dry_run: bool = False):
        self.base_url = base_url
        # Set the API key for litellm only if not in dry-run mode
        if not dry_run:
            if base_url:
                litellm.api_key = "dummy"  # vLLM doesn't require auth
                litellm.api_base = base_url
            else:
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

        # API call tracking
        self.reset_call_counters()

    def reset_call_counters(self):
        """Reset all API call counters"""
        self.call_counters = {
            'inference': 0,  # For generating responses/debate moves
            'scoring': 0,    # For scoring individual sentences
            'judge': 0       # For final debate evaluation
        }

    def get_call_statistics(self):
        """Get current API call statistics"""
        return self.call_counters.copy()

    async def gchat(self, messages, temp=0.8, max_tok=256, call_type='inference'):
        """Make a chat completion call with tracking"""
        if self.dry_run:
            # Return mock response for dry-run mode
            response = self._mock_responses[self._response_counter % len(self._mock_responses)]
            self._response_counter += 1
            # Don't count dry-run calls
            return response

        try:
            # Track the API call
            if call_type in self.call_counters:
                self.call_counters[call_type] += 1

            model_prefix = "groq/" if not self.base_url else "openai/"
            rsp = await litellm.acompletion(
                model=f"{model_prefix}{self.model_name}",
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

    async def batch_gchat(self, requests, call_type='inference'):
        """Make batch chat completion calls with tracking"""
        if self.dry_run:
            # Return mock responses for dry-run mode
            responses = []
            for _ in requests:
                response = self._mock_responses[self._response_counter % len(self._mock_responses)]
                self._response_counter += 1
                responses.append(response)
            return responses

        try:
            # Track the API calls
            if call_type in self.call_counters:
                self.call_counters[call_type] += len(requests)

            model_prefix = "groq/" if not self.base_url else "openai/"
            tasks = []
            for req in requests:
                task = litellm.acompletion(
                    model=f"{model_prefix}{self.model_name}",
                    messages=req['messages'],
                    temperature=req.get('temp', 0.8),
                    max_tokens=req.get('max_tok', 256),
                )
                tasks.append(task)
            responses = await asyncio.gather(*tasks)
            return [rsp.choices[0].message.content.strip() for rsp in responses]
        except Exception as e:
            print(f"Batch API Error: {e}")
            print("Full traceback:")
            traceback.print_exc()
            return ["I maintain my position on this important issue."] * len(requests)

    def run(self, coro):
        """Run a coroutine, handling event loop properly"""
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop is running, create a new one
            return asyncio.run(coro)

# Global instance - will be reconfigured in main based on dry_run flag
api_client = APIClient(os.environ.get("GROQ_API_KEY", "dummy"), "Qwen/Qwen2.5-1.5B-Instruct", base_url=os.environ.get("VLLM_BASE_URL"), dry_run=True)

def configure_api_client(dry_run: bool = False, base_url: str = None):
    """Reconfigure the global API client for dry-run mode or local vLLM"""
    global api_client
    if dry_run:
        api_client = APIClient("dummy", "Qwen/Qwen2.5-1.5B-Instruct", base_url=base_url, dry_run=True)
    else:
        api_client = APIClient(os.environ.get("GROQ_API_KEY"), "Qwen/Qwen2.5-1.5B-Instruct", base_url=base_url, dry_run=False)
