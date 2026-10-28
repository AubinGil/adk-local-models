# Show and Tell draft

I made [adk-local-models](https://github.com/AubinGil/adk-local-models), a direct adapter for Google ADK and local OpenAI-compatible chat-completions servers. ADK's native `OpenAILlm` is the default path for most users. This package is for cases that need no OpenAI SDK, errors as ADK responses, final-only streamed tool calls, truncated-stream rejection, documented profile knobs, and request/reply hashes with advertised server identity.

It supports vLLM, Ollama and llama-server. The vLLM and Ollama profiles were exercised live with one model each; llama-server was tested with fixtures only. Text, streaming, tools, errors and recording are covered by the [tests](tests/test_adapter.py) and [comparison evidence](briefs/007-result.md).

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

I'd welcome testing, reports and contributions, especially with other server configurations.
