# Brief 006 result: Ollama reachable; gemma4:12b absent, stopped as required

The single `/v1/models` read succeeded on the owner's main Ollama, but the
required `gemma4:12b` was not advertised. Brief 006 says to record this and stop,
never pull the model. No completion or Runner request was sent, no substitute
model was selected, and nothing was changed on the server.

Branch `feature/006-ollama-live`, based on `main` at `5620915`.
The reading was captured 2026-10-28, 16:22:16 UTC (12:22:16 EDT), under the owner's
direct `go ollama is available` instruction, just before the updated brief was
read. It used the same endpoint and required model as brief 006. The existing
reading was reused and moved to the brief's path; no repeated identity request.
The capture summary correctly retains its earlier source commit `2e9f363`.

| Check | Result |
|---|---|
| Endpoint | `http://127.0.0.1:11434/v1` |
| Reachable | Yes; identity GET HTTP 200 |
| Identity wall time | 0.291 seconds |
| Required model | `gemma4:12b`, absent from the returned listing |
| Other Gemma models advertised | `gemma4:26b`, `gemma4:e4b`; neither used |
| Identity SHA-256 | `6f8406583ae727e268c0ff1f9b86b52fbc59ebd3d9fe578cd7a725d8cbfb4ce0` |
| Thinking knob accepted/reported | Not tested; no generation request sent |
| Plain/streamed text | Skipped under the missing-model stop rule |
| Plain/streamed tool calls and IDs | Skipped under the missing-model stop rule |
| Plain/streamed Runner round trip | Skipped; prerequisite not met |
| HTTP request count | One GET; zero POSTs; zero retries |

The captured listing uses the same core fields as the fake fixture: `object`,
`data`, and entries with `id`, `object`, `created`, `owned_by`. It contains 24
entries, including local and cloud-tagged names, rather than the fixture's one
fake model. No `Server` header was returned (`server=null` in adapter identity).
The identity schema is less detailed than vLLM's listing with context, root
snapshot and permissions. The adapter parsed the listing and its exact reply
hash matches the recording.

There is no response evidence for finish reasons, token usage, reasoning fields,
SSE framing, tool IDs or session persistence. The summary's planned
`reasoning_effort="none"` reflects the pre-existing profile fixture and general
[Ollama compatibility documentation](https://docs.ollama.com/api/openai-compatibility),
which was consulted before the identity check. It was not transmitted or
validated for this model. Model-specific thinking investigation was not reached.

No adapter/profile correction is indicated by a missing served model. Live
Ollama coverage remains unproven. Further calls require a follow-up owner
instruction after the required model is available or a brief selecting a
different model. This run does not pull, start, reload or otherwise prepare it.
Port 11435, all other servers, and cloud model inference were untouched.

[Readings and method](../runs/006-ollama/README.md),
[identity exchange](../runs/006-ollama/ollama/probe-1/exchange.json),
[summary](../runs/006-ollama/summary.json),
[offline verification](../runs/006-ollama/verification.json).
Source, tests, fixtures and dependencies are unchanged. The gated 17 tests were
not rerun for this evidence-only result. Captured hashes/lengths, missing-model
status, and empty completion samples verify offline; working-tree and staged
diff checks pass. No secrets supplied; nothing pushed.
