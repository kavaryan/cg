import asyncio
import os
import core.api_client as api_mod

# Configure for vLLM (assumes VLLM_BASE_URL is set)
base_url = os.environ.get('VLLM_BASE_URL')
if not base_url:
    print("Error: Set VLLM_BASE_URL environment variable (e.g., export VLLM_BASE_URL=https://your-ngrok-url.ngrok.io/v1)")
    exit(1)

api_mod.configure_api_client(dry_run=False, base_url=base_url)
print(f"Configured API client with base_url: {base_url}")

async def test_gchat():
    messages = [{"role": "user", "content": "Hello, this is a test for the debate tournament."}]
    response = await api_mod.api_client.gchat(messages, temp=0.8, max_tok=100, call_type='inference')
    print("Response from vLLM:")
    print(response)
    stats = api_mod.api_client.get_call_statistics()
    print(f"API Call Stats: {stats}")

# Run the test
asyncio.run(test_gchat())
