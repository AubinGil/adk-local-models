# Ollama Gemma e4b continuation

Owner instruction: `just use a gemma model there theres a coupke`. Selected the
already-advertised `gemma4:e4b`, overriding brief 006's fixed 12b selection without
pulling or creating a model. Captured on 2026-10-28, 16:50:40-16:50:52 UTC.
Only `http://127.0.0.1:11434/v1` was used; no port 11435 or cloud inference.

Nine sequential HTTP exchanges here: one adapter identity GET, text/tools
fixtures each plain/streamed, then two completions per Runner turn in NONE and
SSE modes. With the prior missing-12b GET preserved at the parent path, the entire
assignment used ten HTTP requests, below the twelve-request bound. No retries,
server lifecycle/configuration changes, extra probes, or source/test changes.

The current gated fixtures were used exactly, with the selected model and
`reasoning_effort="none"`. The text fixture retains JSON mode and max_tokens 32;
tools have no JSON mode. Both tool fixture calls parsed, meeting the brief's
prerequisite for Runner. No forced tool choice or other extension was added.

The Runner setup matches brief 005: LlmAgent `local`, fresh InMemorySessionService
per mode (app `adapter_smoke_006`, user `user`, sessions `plain` and `stream`),
user text `Weather in Paris?`, and instruction `Be concise. Use weather once for
the requested city, then answer from its result. Do not call weather again after
receiving its result.` ADK appends the internal-name instruction on the wire.
Generation config: temperature 0, top_p 0.9, max_output_tokens 128; no JSON mime
type or stop sequence. `RunConfig` uses NONE/SSE and max_llm_calls 2. The local
`weather(city: str)` function (docstring: `Get weather for a city.`) logs its
invocation and deterministically returns `{"temperature":20}`.

The adapter was unchanged. Temporary observers wrapped httpx send/raw-read and
the adapter generator to retain bytes/responses, without request transformation,
replacement transport, or retries. An explicit adapter identity read (3-second
timeout) is cached for all calls here; completion timeout is 120 seconds per
operation. An observer permits only this models/chat-completions endpoint and
caps continuation sends at eleven, accounting for the prior GET. Only nine were
needed. No credentials or environment proxies used.

Each exchange directory contains exact `request.bin`, `reply.bin`, and
`exchange.json` with status/headers, timings, entity hashes/lengths and identity
or all ADK requests/responses. Completion metadata is also saved separately in
`custom_metadata.json`. Hashes include SSE framing, exclude HTTP headers and
transfer framing. Inherited `.bin` attributes preserve exact entity bytes.
Each Runner turn contains actual `yielded_events.json`, `session_events.json`
and `tool_executions.json`. `verification.json` is offline verification with no
further requests. Per-exchange wall times include yielding to the consumer.

Sources read 2026-10-28:
[compatibility thinking control](https://docs.ollama.com/api/openai-compatibility)
and [Gemma 4 model documentation](https://ollama.com/library/gemma4).
All eight POSTs accepted `reasoning_effort="none"`; no reasoning output or token
details were reported. This does not establish internal thinking behavior.

See [the updated result](../../../briefs/006-result.md). Parent summary and
verification remain the original missing-model check; this directory's summary
and verification cover the authorized continuation without overwriting it.
