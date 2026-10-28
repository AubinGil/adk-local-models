# Brief 002 result: all configured endpoints unreachable

On 2026-10-28, 14:16:20-14:16:30 UTC (10:16:20-10:16:30 EDT), all four
authorized `/v1/models` probes returned the adapter's cached identity marker
`{"error":"ConnectError"}`. No HTTP response status or body was received.
All three profiles were skipped. **Zero chat-completions requests were sent.**
No retries, server starts/stops, model pulls, reloads, or code/test changes.

Branch: `feature/002-live-smoke`, based on `main` at
`29a84cc`. Readings: [summary](../runs/002-live-smoke/summary.json).

Ollama:

| Check | Result |
|---|---|
| Endpoint | `http://127.0.0.1:11434/v1` |
| Reachable | No; `ConnectError` |
| Configured model | `gemma4:12b` (not verified) |
| Identity hash | Unavailable; no identity reply |
| Text reply ok | Not tested; skipped |
| Tool call ok | Not tested; skipped |
| Streamed ok | Not tested; skipped |
| Knob accepted | Not tested; planned `reasoning_effort="none"` |

Evidence: [probe record](../runs/002-live-smoke/ollama/probe-1/exchange.json).
Port 11435 was not contacted.

vLLM:

| Check | Result |
|---|---|
| Endpoints | `http://localhost:8004/v1`, then `http://localhost:8037/v1` |
| Reachable | Neither; both `ConnectError` |
| Configured models | 8004: `unsloth/gemma-4-12b-it-NVFP4`; 8037: `qwen3.8-27b` (neither verified) |
| Identity hash | Unavailable for both; no identity reply |
| Text reply ok | Not tested; skipped |
| Tool call ok | Not tested; skipped |
| Streamed ok | Not tested; skipped |
| Knob accepted | Not tested; planned `chat_template_kwargs.enable_thinking=false` |

Evidence: [8004 probe](../runs/002-live-smoke/vllm/probe-1/exchange.json),
[8037 probe](../runs/002-live-smoke/vllm/probe-2/exchange.json).

llama-server:

| Check | Result |
|---|---|
| Endpoint | `http://localhost:8080/v1` |
| Reachable | No; `ConnectError` |
| Model | None discovered; no configured chat model was supplied in the brief |
| Identity hash | Unavailable; no identity reply |
| Text reply ok | Not tested; skipped |
| Tool call ok | Not tested; skipped |
| Streamed ok | Not tested; skipped |
| Knob accepted | Not tested; fixture knob was `reasoning_format="none"` |

Evidence: [probe record](../runs/002-live-smoke/llama_server/probe-1/exchange.json).
No Decision2 scoring route was contacted. The fixture knob controls reasoning
format and does not itself prove thinking is disabled, as noted in brief 001.

The only observed difference from the fake-server environment is connection
failure before HTTP. There is no live evidence about field names, finish reasons,
usage, reasoning fields, SSE framing, tool parsing, or JSON-object arguments.
No adapter correction is justified by these readings. Brief 003 can repeat the
authorized smoke after the owner makes a listed server available; this brief
does not infer that a service is stopped or diagnose the cause of refusal.

The unchanged adapter's `_read_identity()` was used for each check, with a
3-second HTTP timeout, `trust_env=False`, `Accept-Encoding: identity`, and no
credentials. A temporary observer recorded the attempted request body and any
raw reply bytes without changing transport behavior. The adapter's cached error
marker, elapsed wall time, and hashes are in each probe record. GET entities are
empty; reply entities are empty because no bytes arrived. Their empty-byte
SHA-256 is **not** an identity hash and does not signify a successful exchange.

Verification: all four recorded request/reply files match their recorded lengths
and SHA-256 values; all profiles have zero completion samples. Source, tests,
fixtures, dependencies and the gated 16-test suite are unchanged from `main`;
tests were not rerun because this brief changes only readings and documentation.
`git diff --check` and the staged diff check pass. Nothing was pushed.
