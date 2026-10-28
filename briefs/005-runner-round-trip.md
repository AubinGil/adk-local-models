# Brief 005 — the fixture split and a live Runner round trip on 8038

**Why.** Brief 004 showed live tool parsing and id preservation hold once JSON mode is off the tool request. Two
things remain unproven: the fixtures still send JSON mode with tools, and no tool has yet been executed and
answered back to a live server through ADK's `Runner`.

**Server and word.** The owner's vLLM on `http://localhost:8038/v1`, `nemotron-3.5-bolt-e4b`, offered on
2026-10-28; the offer covers the requests below. Check, never start, stop or reload.

**Steps.**
1. Model-free first: in `tests/requests.py`, keep JSON mode on the text request and remove it from the tool and
   history requests; regenerate the affected goldens deliberately, show the diff in the delivery note, and keep a
   separate golden that still covers JSON mode with no tools. The 16 tests must pass; add one that asserts the tool
   request body carries no `response_format`.
2. Live, at most six requests, no retries, thinking off as before: one `Runner` turn with `InMemorySessionService`
   and the `weather` function tool against 8038, where the model calls the tool, the tool runs once, the function
   response goes back with the server-issued id, and the model's final text reaches the session; run it once
   non-streamed and once with ADK's streaming mode. Record every exchange under `runs/005-runner-8038/` in brief
   004's shape, plus the session's event list.
3. `briefs/005-result.md`: whether the round trip completed in each mode, the ids on the way out and back, the
   final text, every difference from the fake-server fixtures, and anything the adapter would need to change,
   recorded for a later brief unless it blocks the round trip, in which case fix it with a test and say so.

**Bounds.** One server, one model; the fixture change is the only intended code change. Branch
`feature/005-runner-round-trip` from `main`; commit with the owner's identity and the usual tail; no push;
deliver the branch and the SHA, then stop.
