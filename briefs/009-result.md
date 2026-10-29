# Brief 009 result: smoke passes; reasoning knob fails

The llama_server adapter completed all four smoke requests and both Runner round trips on LFM3-1.7B Q4_K_M. The actual binary reports 0.8.0-dev (build 1, commit 8642541), rather than the brief's b11960. Both tests with reasoning_format none returned HTTP 400. Public surfaces and version remain unchanged under step 5's failure rule; no package code changed.

| Request | Result |
|---|---|
| Text plain / SSE, reasoning off | HTTP 200, STOP; JSON text {"weather": "Paris"} |
| Tools plain / SSE, reasoning off | HTTP 200, STOP; weather with object city Paris parsed, IDs retained |
| Runner plain | Two HTTP 200 completions, one local tool execution, four session events, final answer persisted |
| Runner SSE | Two HTTP 200 completions, one local tool execution, four session events, final answer persisted |
| Text with reasoning_format none, reasoning off | HTTP 400: Failed to initialize samplers: std::exception |
| Text with no knob, default reasoning | HTTP 200, length/MAX_TOKENS; reasoning_content present, answer empty at 32 tokens |
| Text with reasoning_format none, default reasoning | Same HTTP 400 sampler initialization error |

Both Runner final texts say the weather in Paris is 20 degrees Celsius. Server-issued call IDs match the tool return messages in both modes. Tool calls appear only in final adapter responses; SSE partials carry progress. Text/tool finish mappings and basic usage fields parsed without adapter changes. Unlike the fixture's fixed identity listing, the live listing carries architecture and GGUF metadata and reports Server llama.cpp. Stream entity bytes include SSE framing and [DONE]. Exact field details, timings, token counts and yielded events remain in the recorded exchanges.

The request-level none knob did not yield raw answer text in this fixture: it changed a successful plain response into an error under both server settings. This establishes the observed combination only, not the cause of the server error or behavior without JSON mode. No retry, forced tool choice, altered template, or additional diagnostic completion was sent.

Two identity reads and eleven completions, below bounds. All 13 request/reply hashes and partial prefix hashes verified offline; both return-path IDs and once-only tool execution verified. The 17 model-free tests passed. Both started servers and the workstation tunnel were stopped; final process reading was empty. No push or release action.

[Run readings](../runs/009-llama-server/README.md), [summary](../runs/009-llama-server/summary.json), [verification](../runs/009-llama-server/verification.json).

## Gate (reviewer, 2026-10-28, at 127a3b0): accepted within bounds; the caveat stays until brief 010

Reproduced on the branch: 17 tests pass; `git diff --check` clean; no public surface, package file or test
changed, as step 5's failure rule required. The reviewer recomputed the SHA-256 of all 26 request and reply
entity files against their records: 26 match. Both `Runner` turns show one tool execution and four session events
each, and the final answers persist. The Jetson was left as found: no llama-server process, port 8111 closed, the
server log ending in its clean exit. Two identity reads and eleven completions, inside the bounds.

**What this proves.** The `llama_server` profile works live: identity, text and tools plain and streamed, tool
ids preserved, both `Runner` round trips complete, on LFM3-1.7B Q4_K_M under llama.cpp 0.8.0 with `--jinja
--reasoning off`. The binary's version string `0.8.0-dev (build 1, commit 8642541)` is tag `b11960` = `v0.8.0`
built from a grafted clone, so the build number is not available to it; the commit is the tag's.

**What it also found.** The profile's documented knob, `reasoning_format: none`, drew HTTP 400 `Failed to
initialize samplers` from the server with reasoning off and with reasoning on. Every such request also carried the
fixture's `response_format: json_object`, so the cause is not isolated; Codex sent no diagnostic request, as the
bounds required. The README's llama-server example recommends exactly that knob, so the caveat cannot come off
until the knob is settled. That is brief 010, written at this gate: four requests without JSON mode, the package
fixed to the finding either way, then the public surfaces and 0.1.1.

**Bounds.** One model, one server build, one knob tested in one combination. The run's default-reasoning request
confirms what the Jetson probes showed: LFM3-1.7B spends the 32-token fixture budget in `reasoning_content` and
returns an empty answer unless the server runs with `--reasoning off`.

