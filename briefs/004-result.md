# Brief 004 result: tool parsing and IDs hold live without JSON mode

All four authorized requests to `http://localhost:8038/v1`, model
`nemotron-3.5-bolt-e4b`, returned HTTP 200 with exactly one parsed `weather` call,
JSON-object arguments `{"city":"Paris"}`, and a nonempty server-issued ID. The
adapter preserved each raw ID exactly. No ordinary text content was returned.

Run: 2026-10-28 15:09:54-15:09:57 UTC (11:09:54-11:09:57 EDT), branch
`feature/004-tool-call`, based on `main` at `4b2a4ae`. One identity GET, then four
sequential completion POSTs; no retries, tool execution or server changes.

| Variant | HTTP | Wall seconds | Raw finish -> ADK | Parsed call / object argument | Preserved raw ID |
|---|---|---|---|---|---|
| Choice omitted, plain | 200 | 0.804 | `tool_calls` -> `STOP` | `weather` / `{"city":"Paris"}` | `chatcmpl-tool-9e4539e09558423f` |
| Choice omitted, streamed | 200 | 0.630 | `tool_calls` -> `STOP` | `weather` / `{"city":"Paris"}` | `chatcmpl-tool-8e0c30c87d96ef75` |
| Choice required, plain | 200 | 0.627 | `tool_calls` -> `STOP` | `weather` / `{"city":"Paris"}` | `chatcmpl-tool-a2c091cef6f789f3` |
| Choice required, streamed | 200 | 0.642 | `tool_calls` -> `STOP` | `weather` / `{"city":"Paris"}` | `chatcmpl-tool-ab4985e89bdb3d22` |

The adapter's identity GET took 0.480 seconds, returned HTTP 200 and advertised
the requested model with max context 16384. Its raw reply SHA-256 is
`bd285be64578744b4b4aea42ef09dcf91fa27c8534fca4b6a81b2f420f9cf883`.
The server header is `uvicorn` and completion fingerprint is
`vllm-0.31.0-5ad08979`. Identity is recorded anew for this run rather than assumed
to equal brief 003's listing.

The required value is documented by [vLLM 0.31.0, Required Function Calling](https://docs.vllm.ai/en/v0.31.0/features/tool_calling/#required-function-calling):
`tool_choice="required"` requires at least one tool call. It was supplied through
the existing `extra_body`, without changing the adapter. Thinking remained off
using the [NVIDIA model card's Reasoning Off control](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16),
`chat_template_kwargs.enable_thinking=false`, as checked in brief 003. All four
responses reported zero reasoning tokens and `reasoning=null` where present.

The only run-specific request changes from the tool fixture were removal of JSON
mode, the model ID, the stream flag/options, and (for the second variant) required
tool choice. Temperature, top_p, token cap, stop sequence, instructions and tool
schema were preserved. Without JSON mode, even the omitted-choice pair produced
proper tool calls. This supports removing the shared JSON mime type from the
tool fixture in a **later brief**, while retaining separate JSON-output coverage.
It is evidence for this server/model/request, not a claim that JSON mode and tools
cannot coexist on every backend. No fixture, golden, test or source was changed.

Streaming held live: each stream yielded three empty progress chunks with
`partial=true`, no exposed tool calls, and then one complete `partial=false`
response carrying the call. Raw SSE first supplied the function name and ID at
index 0, then the argument string in two fragments. The adapter assembled the
JSON object and preserved the raw ID from that stream. Usage arrived separately
with `choices=[]`, followed by `[DONE]`; SSE used LF blank-line framing. All four
replies reported 66 prompt, 13 completion and 79 total tokens.

The omitted plain reply has `content=null`; the required plain reply has
`content=""`. Both correctly become a function-only ADK content object. Plain and
streamed final content, finish reason and usage agree **after normalizing their
distinct server-issued call IDs**. Actual IDs are never overwritten in recordings
or adapter responses. Recording metadata also differs as expected. Complete
request/reply hashes and all partial-prefix hashes verify against captured bytes.

No adapter correction is indicated by these replies. Live inbound tool parsing
and ID preservation now have evidence for vLLM on 8038. No tool was executed and
no function response was sent back, so a complete live Runner tool round trip and
return-path ID matching remain outside this brief. Other profiles and nonempty
reasoning remain untested live. No server-side change is needed to explain these
successful calls.

[Readings and method](../runs/004-tool-call-8038/README.md),
[summary](../runs/004-tool-call-8038/summary.json),
[offline verification](../runs/004-tool-call-8038/verification.json).
Source, tests, fixtures and dependencies are unchanged from `main`; the gated
16 tests were not rerun for this readings-only brief. Artifact verification,
working-tree and staged diff checks pass. No secrets supplied; nothing pushed.
