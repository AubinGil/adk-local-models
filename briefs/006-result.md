# Brief 006 result: Ollama Gemma smoke and both Runner round trips complete

The owner authorized using an available Gemma model after the initial missing
`gemma4:12b` result below. Selected **`gemma4:e4b`**, already advertised on the
same main Ollama endpoint. This direct instruction supersedes only the brief's
fixed-model stop condition. No pull, model creation, server start/stop/reload,
native-endpoint call, cloud inference or request retry was made.

Continued on `feature/006-ollama-live` from the initial result commit `6e291a1`.
The new run is under `runs/006-ollama/gemma4-e4b/`; the first identity reading and
its original summary are preserved at the parent path. Continuation:
2026-10-28, 16:50:40-16:50:52 UTC (12:50:40-12:50:52 EDT). Nine new requests:
one identity GET, four fixture POSTs, and four Runner POSTs. Including the initial
identity GET, **ten total HTTP requests**, below the brief's twelve-request limit.

| Check | Ollama result |
|---|---|
| Endpoint | `http://127.0.0.1:11434/v1`; all nine continuation exchanges HTTP 200 |
| Authorized model | `gemma4:e4b`, confirmed in the new identity read |
| Identity SHA-256 | `6f8406583ae727e268c0ff1f9b86b52fbc59ebd3d9fe578cd7a725d8cbfb4ce0` (same listing bytes as initial check) |
| Fingerprint / Server header | `fp_ollama` in completions; no Server header |
| Thinking knob | `reasoning_effort="none"` accepted on all eight POSTs; no reasoning output/detail fields observed |
| Text plain / streamed | Both parsed; `length` -> `MAX_TOKENS`; equal aggregate text and usage; JSON content truncated at 32 tokens |
| Tool plain / streamed | Both parsed `weather({"city":"Paris"})`; nonempty server IDs preserved; `tool_calls` -> `STOP` |
| Runner plain / SSE | Both complete; local tool runs once; return-path ID matches; final text reaches session |
| Fixes | No adapter, profile, fixture, test or dependency changes needed |

| Exchange | Wall seconds | Prompt / completion / total tokens | Raw finish |
|---|---|---|---|
| Identity | 0.288 | N/A | N/A |
| Fixture text plain | 9.293 | 21 / 32 / 53 | `length` |
| Fixture text streamed | 0.432 | 21 / 32 / 53 | `length` |
| Fixture tools plain | 0.265 | 65 / 13 / 78 | `tool_calls` |
| Fixture tools streamed | 0.258 | 65 / 13 / 78 | `tool_calls` |
| Runner plain call | 0.281 | 99 / 13 / 112 | `tool_calls` |
| Runner plain answer | 0.266 | 128 / 11 / 139 | `stop` |
| Runner SSE call | 0.267 | 99 / 13 / 112 | `tool_calls` |
| Runner SSE answer | 0.264 | 128 / 11 / 139 | `stop` |

These are observed wall times, not performance benchmarks or a diagnosis of the
first request's longer duration. No answer-quality judgement.

| Tool call | Raw ID preserved into ADK | Same ID on return wire message |
|---|---|---|
| Fixture plain | `call_6dd7cnst` | No tool executed in fixture smoke |
| Fixture streamed | `call_8ueolpu5` | No tool executed in fixture smoke |
| Runner plain | `call_hd5znadm` | `call_hd5znadm` |
| Runner SSE | `call_5xrbedan` | `call_5xrbedan` |

Both Runner modes use the brief 005 setup: a local deterministic `weather(city)`
returns `{"temperature":20}`, temperature 0, top_p 0.9, max_output_tokens 128,
no JSON mode or stop sequence, and an instruction to call weather once then
answer from its result. Each turn has two completion exchanges, one execution
with `city="Paris"`, and four persisted events: user, call, function response,
final answer. Both sessions end with **`The weather in Paris is 20 degrees.`**
Plain yields 3 output events; SSE yields 14, including progress that is not
persisted. No external weather service was queried.

Thinking control sources, read for this continuation:
[Ollama OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility)
documents `reasoning_effort` and `"none"` requesting false for boolean thinking
control. The [Ollama Gemma 4 model page](https://ollama.com/library/gemma4)
describes template-managed thinking and disabling its trigger. The profile's
documented compatibility control `reasoning_effort="none"` was used, with no
manual thought tokens or native `think` / `keep_alive` fields. All requests
accepted it, and no reasoning fields or thought text appeared in these replies.
Unlike vLLM's zero reasoning-token detail, Ollama supplied no such count, so this
is acceptance/no-observed-reasoning evidence, not proof of internal behavior.

Differences from fixtures and vLLM:

- The corrected fixtures were sent unchanged except for model selection, stream
  flag/options and the Ollama knob: JSON mode remains on text, absent on tools.
  Text is truncated JSON at the 32-token cap, like the vLLM fixture smoke. Tool
  calls return object arguments rather than ordinary JSON text. No forced tool
  choice was needed. Parsed fixtures' content, finish and usage match between
  modes after accounting for distinct server-issued IDs and wire metadata.
- Core message, choice, finish, tool and usage fields are compatible. Ollama IDs
  use `call_*`; vLLM issued `chatcmpl-tool-*`; the fixture uses `call_weather`.
  Ollama plain tool entries additionally have `index:0`; arguments are compact
  JSON strings. The adapter preserved all IDs and decoded the strings to objects.
- Ollama identity is the shorter model listing already described in the initial
  result; completions expose `system_fingerprint="fp_ollama"`. Optional/null
  message fields and extended vLLM response fields are absent rather than null.
  This causes no mapper failure. Exact raw fields remain in the recordings.
- Ollama usage includes `prompt_tokens_details.cached_tokens`, which varies
  between plain/streamed requests, and SSE usage events include `timings`.
  Those details are ignored by the current mapping; the three mapped counts
  above match within each pair. Counts differ from fixture 8/3/11 and from
  vLLM's prompt tokenization. No reasoning-token details were returned.
- SSE uses LF-delimited data events and `[DONE]`, with separate usage in a
  `choices=[]` event. The text fixture emits 32 nonempty text partials. Each tool
  stream emits one complete tool delta (plus an empty finish delta), yielding
  one empty progress chunk and a final call. This differs from vLLM's three
  fragmented tool deltas and from the fake fragment fixture. The existing
  accumulator handles it. Runner's final text emits ten partials and one final
  aggregate; only complete events persist, and the tool executes once.
- Runner final text differs from vLLM's `The weather in Paris is 20.` and the
  fake `Hello café!`; both Ollama modes agree. A full live return-path ID and
  session-persistence check now holds for this Ollama model as well as vLLM.

No blocking behavior or correction was found. Nonempty reasoning replay and
llama-server live coverage remain outside this result. Source/tests/dependencies
are unchanged and the gated 17 tests were not rerun. Offline checks verify all
captured entities, metadata/prefix hashes, fixture shapes, raw-to-ADK IDs, once-only
execution and matching return IDs, final session contents, and the ten-request
total. Working-tree and staged diff checks pass. No secrets supplied or push.

[Continuation method](../runs/006-ollama/gemma4-e4b/README.md),
[summary](../runs/006-ollama/gemma4-e4b/summary.json),
[verification](../runs/006-ollama/gemma4-e4b/verification.json).

## Initial stop result (historical; superseded by owner's model substitution)

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

## Gate (reviewer, 2026-10-28): accepted within stated bounds; the `ollama` profile holds live on Gemma 4 E4B

Reproduced at c534f31 on `feature/006-ollama-live`: readings and notes only, no source, test, fixture or dependency
changed; `git diff --check` clean. The brief's stop condition was honoured first: commit 6e291a1 recorded that
`gemma4:12b` was absent and stopped; the continuation on `gemma4:e4b` rests on the owner's direct word to Codex,
and the model list on the server shows that tag present since 2026-10-26, so nothing was pulled. The reviewer
recomputed every recorded hash from the raw bytes: ten exchanges, ten matches; the identity reply lists
`gemma4:e4b` and not `gemma4:12b`. Both `Runner` round trips carry the tool message back under the id the server
issued (`call_hd5znadm`, `call_5xrbedan`) with the function's result, and the final text reached each session.
The thinking knob is the one Ollama's compatibility page documents, `reasoning_effort`, accepted on every request
with no reasoning fields in the replies. Ten requests, under the brief's twelve.

**Bounds.** One model, not the one the brief named; Ollama reports no reasoning-token count, so "thinking off" is
acceptance plus absence, not a measurement; the llama-server profile still has no live evidence. The adapter now
has live evidence on two of its three profiles with no code change between them. As briefed, Codex touched
nothing on the server and stopped.
