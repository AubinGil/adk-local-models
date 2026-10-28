# Brief 006 — the `ollama` profile, live

**Goal.** Everything briefs 003 to 005 proved for vLLM, now for the `ollama` profile against the owner's main
Ollama with `gemma4:12b`: identity, text, streaming, tool calls with ids, and a `Runner` round trip. The owner
starts Ollama and says so; the owner's word for the requests is given (2026-10-28, "Maybe ill finish the ollama
test first"). The server is the owner's: check, never start, stop, pull or reload; if `gemma4:12b` is not present,
record it and stop, never pull it.

**Server.** `http://127.0.0.1:11434/v1`, profile `ollama`, model `gemma4:12b`. The side Ollama on 11435 serves a
decision model and is not used.

**Steps, each with readings under `runs/006-ollama/` in brief 004's shape and no retries.**
1. Identity: the adapter's `/v1/models` read, hash recorded; confirm `gemma4:12b` is listed.
2. The thinking knob: Ollama's compatibility endpoint documents `reasoning_effort` for thinking-capable models.
   Read what Ollama documents for Gemma 4 and send the documented value or nothing, citing the page; nothing is
   invented. Record whether the server accepted it and what it reported.
3. Text: the fixtures' plain text request (with JSON mode, as the fixture has it), once non-streamed and once
   streamed.
4. Tool: the fixtures' tool request (no JSON mode, as split in brief 005), once non-streamed and once streamed; if
   no tool call comes back, record the raw reply and name what Ollama documents about tool calling for this model
   and this endpoint; do not change the server.
5. Round trip: one `Runner` turn with the `weather` function tool, once non-streamed and once in ADK's streaming
   mode, as in brief 005, only if step 4 produced a parsed tool call.
6. `briefs/006-result.md`: one table of the checks, the timing, every difference from the vLLM readings and from
   the fixtures (field names, finish reasons, usage, reasoning fields, streaming framing, tool-call ids), and
   what the adapter or the `ollama` profile would need to change, recorded for a later brief unless it blocks a
   step, in which case fix it with a test and say so.

**Bounds.** At most twelve requests; one server, one model; no code change unless a step is blocked. Branch
`feature/006-ollama-live` from `main`; commit with the owner's identity and the usual tail; no push; deliver the
branch and the SHA, then stop.
