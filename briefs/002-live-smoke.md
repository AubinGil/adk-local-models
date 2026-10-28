# Brief 002 — live smoke, one request per profile

**Goal.** Show the gated adapter working against the owner's real servers, one profile at a time, touching nothing
on them. The owner's word for these calls is given (2026-10-28: "yes write brief002"). The servers are the
owner's: check, never start, stop, pull or reload.

**Steps.**
1. Check-only, per profile, with `GET /v1/models` on the configured endpoint, recording reachable or not and the
   identity hash the adapter computes:
   - `ollama`: `http://127.0.0.1:11434/v1`, model `gemma4:12b` (the owner's main Ollama; the side Ollama on
     11435 serves a decision model, not chat, and is not used).
   - `vllm`: whichever of `http://localhost:8004/v1` (`unsloth/gemma-4-12b-it-NVFP4`) or
     `http://localhost:8037/v1` (`qwen3.8-27b`) answers; both may be down, in which case the profile is recorded
     as not reachable and skipped.
   - `llama_server`: no chat-capable llama-server is known to be running (the Decision2 server speaks a scoring
     route, not chat completions); record not reachable unless one answers on `http://localhost:8080/v1`.
   A server that does not answer is recorded and skipped, never started.
2. For each reachable server: the fixtures' plain text request and the request with the `weather` tool from
   `tests/requests.py`, each once non-streamed and once streamed, with thinking turned off through that profile's
   documented knob; no retries; one request at a time. Record under `runs/002-live-smoke/<profile>/`: the exact
   request bytes, the raw reply bytes, the adapter's `custom_metadata` (hashes, identity, profile), wall time, and
   whether a tool call came back parsed with a JSON-object argument. The folder is committed; it holds no secrets.
3. `briefs/002-result.md`: one table per profile (reachable, model, identity hash, text reply ok, tool call ok,
   streamed ok, knob accepted), every difference between the live replies and the fixtures' assumptions (field
   names, finish reasons, usage, reasoning fields, SSE framing), and what the adapter would need to change, if
   anything, recorded for brief 003 and not fixed here.

**Bounds.** No code change in this brief; the 16 tests stay as gated. One model per server, one request shape,
no quality judgement of the answers. Branch `feature/002-live-smoke` from `main`; commit with the owner's
identity and the usual tail; no push; deliver the branch and the SHA, then stop.
