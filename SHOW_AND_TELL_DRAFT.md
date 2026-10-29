# adk-local-models: A direct alternative for local inference with Google ADK

Hi everyone!

I've been experimenting with running Google ADK agents using locally hosted models through vLLM and Ollama.

Google ADK already provides options for non-Gemini models, including LiteLLM and its native `OpenAILlm`
integration. I wanted to explore a more direct approach with a small, explicit integration layer, using neither
LiteLLM nor the OpenAI Python SDK.

So I built adk-local-models, an Apache 2.0-licensed Python adapter implementing ADK's `BaseLlm` interface.

What it supports:

- vLLM, Ollama, and llama-server profiles
- Streaming and function calling
- Integration with ADK's `LlmAgent` and `Runner`
- Tool calls held until the final streamed response
- Detection of truncated streams
- ADK-compatible error responses
- Request/reply byte hashes and server identity metadata

A minimal example:

```python
import asyncio
from adk_local_models import OpenAICompatibleLlm
from google.adk.models.llm_request import LlmRequest
from google.genai import types

llm = OpenAICompatibleLlm(profile="vllm", base_url="http://localhost:8000/v1", model="your-model")
request = LlmRequest(contents=[types.Content(role="user", parts=[types.Part(text="Hello")])])
async def main():
    async for reply in llm.generate_content_async(request):
        print(reply)
asyncio.run(main())
```

I also compared the adapter against Google's native `OpenAILlm`. Both completed live ADK `Runner` tests with
Ollama and vLLM. The native implementation offers additional functionality, including image inputs,
reasoning-token usage, and strict schema output. My adapter focuses on a narrower set of requirements,
particularly explicit local-server behavior and traceability.

This isn't intended to replace LiteLLM or Google's native integration. It's simply another option for developers
who prefer these specific behaviors when working with local inference servers.

The llama-server profile was validated live on one model, LFM3-1.7B Q4_K_M, with llama.cpp 0.8.0 (tag b11960) and `--jinja --reasoning off`; see the [recorded run](runs/009-llama-server/).

Repository: https://github.com/AubinGil/adk-local-models

I'd welcome feedback, compatibility testing, and contributions from anyone working with local models in ADK!
