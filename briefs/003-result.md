# Brief 003 result: live text/stream mapping works; no tool call observed

Executed 2026-10-28, 14:58:22-14:58:26 UTC (10:58:22-10:58:26 EDT) on
`feature/003-live-smoke`, based on `main` at `558fcbd`. Exactly one identity GET
and four sequential completion POSTs to the offered server. No retries, server
configuration/lifecycle changes, tool execution, or adapter/test changes.

| Check | vLLM result |
|---|---|
| Endpoint reachable | Yes, `http://localhost:8038/v1`; identity GET HTTP 200 |
| Model | Advertised and requested `nemotron-3.5-bolt-e4b`; advertised max context 16384 |
| Identity SHA-256 | `3dd19048c50e7169dd3d5537be853c3990b9dd34eadb342daa48f002a64d2695` |
| Server information | `Server: uvicorn`; completion fingerprint `vllm-0.31.0-5ad08979` |
| Text reply ok | Mapping/transport yes, plain and streamed HTTP 200; both truncated at 32 tokens (`length` -> `MAX_TOKENS`) |
| Tool call ok | Not demonstrated: both HTTP 200 replies were text, with no `tool_calls` or function call |
| Streamed ok | Yes: 10 text partials / 3 tool-request text partials, then one `partial=false` aggregate; each equals its plain counterpart excluding recording metadata |
| Knob accepted | All four accepted `chat_template_kwargs.enable_thinking=false`; reported `reasoning_tokens=0` |
| Wire recording | All request/reply hashes match adapter metadata; identity hash matches raw GET reply |

| Request | HTTP | Wall seconds | Raw finish reason | Prompt / completion / total tokens | Parsed tool calls |
|---|---|---|---|---|---|
| Text, plain | 200 | 1.751 | `length` | 22 / 32 / 54 | 0 |
| Text, streamed | 200 | 0.666 | `length` | 22 / 32 / 54 | 0 |
| Weather tool, plain | 200 | 0.539 | `stop` | 66 / 7 / 73 | 0 |
| Weather tool, streamed | 200 | 0.521 | `stop` | 66 / 7 / 73 | 0 |

The identity GET took 0.489 seconds. These are observations, not latency or
answer-quality benchmarks. [Readings and method](../runs/003-live-smoke-8038/README.md),
[summary](../runs/003-live-smoke-8038/summary.json),
[offline verification](../runs/003-live-smoke-8038/verification.json).

The thinking knob was checked against the NVIDIA BF16 model card's **API Client /
Reasoning Off** example before sending requests:
https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16
(accessed 2026-10-28). It documents `enable_thinking=False` inside
`chat_template_kwargs`. The fixture's knob matches it. Other example settings,
such as larger token limits and `skip_special_tokens`, were not added. The zero
reasoning-token reports are consistent with thinking off; this is not an audit
of the server's configured template or parser.

Differences from fixture assumptions and implications for a later brief:

- The fixture text response ends with `stop`; the live text response ends with
  `length` after the unchanged 32-token cap. The adapter maps this correctly to
  `MAX_TOKENS`. Its content is an incomplete JSON document. JSON response mode
  does not remove the token limit, and the adapter does not validate generated
  JSON. No output repair, cap increase or retry was attempted.
- The tool fixture returns a `weather` tool call, its ID and object arguments,
  with `finish_reason="tool_calls"`. Live tool requests instead return ordinary
  content `{"city": "Paris"}`, `finish_reason="stop"`, and no `tool_calls` field.
  `function_call` is null. The JSON object is text, not a parsed function argument;
  it must not be promoted to a tool call by the adapter. Both modes agree. There
  was no HTTP rejection, so the brief's tool-pair stop condition did not trigger.
  These readings cannot determine whether model selection, JSON mode, optional
  tool choice, or server parser/template settings caused the absence. A later
  brief needs an explicitly authorized request/configuration investigation to
  prove live tool-call parsing. No adapter correction is justified by this alone.
- Core field names are compatible: `choices`, `message.content`, `delta.content`,
  `finish_reason`, `prompt_tokens`, `completion_tokens`, `total_tokens`. Live
  replies also include IDs, model, creation time, fingerprint and optional/null
  fields absent from the small fixtures (see raw replies). The adapter ignores
  unknown fields as intended. Identity includes root snapshot path, permissions,
  creation time and max context, rather than just the fixture's minimal listing.
- Live non-streamed messages have `reasoning=null`; usage has
  `completion_tokens_details.reasoning_tokens=0`. Non-streamed usage also has
  `prompt_tokens_details=null`. The adapter retains only the three documented
  token counts, without mapping reasoning-token details. This run does not test
  nonempty reasoning fields or reasoning replay.
- Live SSE uses LF-delimited `data: ...` events separated by blank lines, ends
  in `[DONE]`, and sends usage in an extra event with `choices=[]`. Those shapes
  match the fixture contract. The initial role/empty-content event is ignored;
  chunk boundaries differ (10 or 3 nonempty text deltas). Finish reasons appear
  on the last content delta rather than in a separate empty delta. The parser
  handles both. There are 13 text-stream events and 6 tools-stream events,
  including the final `[DONE]`; no tool-delta stream was observed.
- Actual token counts differ from fixture 8/3/11. Plain and streamed final usage
  match for each pair. Complete semantic responses match too; wire hashes and
  raw IDs necessarily differ. All partial reply hashes are valid received-byte
  prefix hashes, and all complete hashes match the captured entities.

No adapter change is needed for the observed text, length-stop, usage or SSE
shapes. Live tool mapping, a live Runner tool turn, other profiles, and nonempty
reasoning remain unproven. The 16 gated tests are unchanged and were not rerun
for this readings-only brief. Source/test/dependency diffs against `main` are
empty; artifact verification and working-tree/staged whitespace checks pass.
No secrets were supplied or recorded. Nothing was pushed.
