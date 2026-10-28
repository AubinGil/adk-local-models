# adk-local-models

`OpenAICompatibleLlm(BaseLlm)` maps Google ADK text and function tools directly to
local OpenAI-compatible chat completions. No LiteLLM or OpenAI SDK is installed.
Python 3.11+, Apache-2.0. Brief 001 is model-free; no owner's server was contacted.

Install in an isolated environment (do not install ADK's `extensions` extra):

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m unittest discover -v
```

The only declared runtime dependency is `google-adk>=2.13.0,<3`. Tested with ADK
2.13.0 and google-genai 2.33.0. The transport uses ADK's existing `httpx` dependency;
tests use standard-library `unittest`. Installation does not start a server.

Each example below is ten lines and assumes an already configured server.
`base_url` is the API root **including `/v1`**, with an optional trailing slash.
The server's actual model name is supplied separately. Examples make calls only
when explicitly run.

vLLM:

```python
import asyncio
from adk_local_models import OpenAICompatibleLlm
from google.adk.models.llm_request import LlmRequest
from google.genai import types
llm = OpenAICompatibleLlm(profile="vllm", base_url="http://localhost:8000/v1",
    model="your-model", extra_body={"chat_template_kwargs": {"enable_thinking": False}})
request = LlmRequest(contents=[types.Content(role="user", parts=[types.Part(text="Hello")])])
async def main():
    async for reply in llm.generate_content_async(request): print(reply)
asyncio.run(main())
```

Ollama:

```python
import asyncio
from adk_local_models import OpenAICompatibleLlm
from google.adk.models.llm_request import LlmRequest
from google.genai import types
llm = OpenAICompatibleLlm(profile="ollama", base_url="http://localhost:11434/v1",
    model="your-model", extra_body={"reasoning_effort": "none"})
request = LlmRequest(contents=[types.Content(role="user", parts=[types.Part(text="Hello")])])
async def main():
    async for reply in llm.generate_content_async(request): print(reply)
asyncio.run(main())
```

llama-server:

```python
import asyncio
from adk_local_models import OpenAICompatibleLlm
from google.adk.models.llm_request import LlmRequest
from google.genai import types
llm = OpenAICompatibleLlm(profile="llama_server", base_url="http://localhost:8080/v1",
    model="your-model", extra_body={"reasoning_format": "none"})
request = LlmRequest(contents=[types.Content(role="user", parts=[types.Part(text="Hello")])])
async def main():
    async for reply in llm.generate_content_async(request): print(reply)
asyncio.run(main())
```

Pass the instance as `LlmAgent(model=llm, tools=[your_function], ...)`. For prefix
resolution, explicitly call `LLMRegistry.register(OpenAICompatibleLlm)` from
`google.adk.models.registry`. The registered patterns are `vllm/.+`, `ollama/.+`,
and `llama-server/.+`; construction strips the prefix and selects that profile's
default local URL. An explicit instance is recommended for custom URLs/keys.
Importing this package does not alter ADK's registry.

`api_key` is optional and becomes a bearer header; it is excluded from model
serialization and repr. `timeout` defaults to 60 seconds per HTTP operation.
`extra_body` copies extensions, rejecting collisions with mapped fields and
known knobs belonging to another profile. No thinking knob is sent by default:
model/template support must be checked by the caller.

The documented controls and server prerequisites are cited in
[profiles.py](src/adk_local_models/profiles.py). See
[vLLM reasoning](https://docs.vllm.ai/en/v0.22.0/features/reasoning_outputs/),
[Ollama compatibility](https://docs.ollama.com/api/openai-compatibility), and
[llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).
Ollama's `keep_alive` and native `think` fields are not documented for chat
completions and are rejected here. llama-server tools require an owner-configured
`--jinja` and a tool-capable template. `reasoning_format="none"` returns raw text;
it does not itself disable thinking. This package never configures servers.

`stream=False` yields exactly one response with `partial=False`. `stream=True`
yields text deltas or empty progress chunks for tool deltas with `partial=True`,
then one complete response with `partial=False`. Tools appear only in the final
response. Do not concatenate final content onto partial text: final content
contains the entire output. Final semantic fields match non-streamed output for
equivalent server replies; recording hashes necessarily differ.

Every response's `custom_metadata` contains `request_sha256`, `reply_sha256`,
`server_identity`, `profile`, and `reply_complete`. Hashes cover exact UTF-8 POST
entity bytes and raw response entity bytes (including SSE framing), excluding
HTTP headers and transfer chunk framing. Partial reply hashes cover bytes received
so far with `reply_complete=False`. Transport failures hash any received prefix,
or empty bytes if none arrived. Invalid requests hash empty request bytes because
no request was sent. Completed malformed replies have `reply_complete=True`;
this flag describes receipt, not validity.

Identity is the `/v1/models` JSON, its raw SHA-256, and the `Server` header, read
once per instance under a concurrency lock. A failed probe is cached as an error
marker; generation can still proceed. This is advertised information, not an
attestation or server version guarantee. Use a new instance after changing the
server. Environment proxies are ignored and redirects are not followed. Raw
bytes remain in fake-server logs in tests; production responses carry hashes.

HTTP errors, transport failures, and malformed replies yield error responses.
Known finish reasons map to `STOP`, `MAX_TOKENS`, or `SAFETY`; unknown reasons map
to `OTHER`. Usage maps to prompt, candidates, and total token counts. Tool IDs
are retained; ID-less history calls receive deterministic IDs and ID-less
responses must match exactly one pending call by name.

Not covered: live/bidirectional API (`connect()` remains unimplemented), images,
audio, reasoning-content replay, server lifecycle management, or structured-output
enforcement beyond `application/json` mapping to `response_format=json_object`.
ADK output schemas are not enforced; `capabilities.output_schema_and_tools=False`.
Unsupported content parts yield errors rather than being discarded. No live
compatibility claims are made before brief 002.

Review design issues and dependency licenses in [the delivery note](briefs/001-delivery.md).
