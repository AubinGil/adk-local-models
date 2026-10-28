# Brief 004 — the tool call, with JSON mode out of the way

**Why.** Brief 003's two tool requests carried `response_format: json_object` together with `tools`, because the
fixtures' shared generation config sets a JSON mime type on every request. A server in JSON mode constrains the
reply to a JSON object, and the model answered with the argument object as text, `{"city": "Paris"}`, with no
`tool_calls`. That explains the absence at least as well as any server-side parser setting, and the two must be
separated before anyone touches the server.

**Server and word.** The same server as brief 003, `http://localhost:8038/v1`, `nemotron-3.5-bolt-e4b`, offered by
the owner on 2026-10-28 for this smoke; the offer covers these two requests. Check, never start, stop or reload.

**Steps.**
1. Build a run-specific request from `tests/requests.py`'s tool request with `response_mime_type` unset, so no
   `response_format` is sent; `tools` present; `tool_choice` absent, then a second variant with `tool_choice`
   set to the documented value that requires a function call, citing vLLM's tool-use page for that value.
   The committed fixtures, goldens and tests stay as they are.
2. Send each variant once non-streamed and once streamed; no retries; thinking off as in 003.
3. Readings under `runs/004-tool-call-8038/` in brief 003's shape (request bytes, raw reply bytes,
   `custom_metadata`, wall time, parsed tool call or not).
4. `briefs/004-result.md`: for each variant, whether a parsed `tool_calls` entry came back with a JSON-object
   argument and an id, the raw content otherwise, and the finish reason. If no variant yields a tool call, say
   so and name what the server would need on its side, from vLLM's documentation, for the owner to decide; do
   not change the server. If a tool call comes back, say whether the adapter's parsing and id handling held
   live, and whether the fixtures' shared JSON mime type should move off the tool request in a later brief.

**Bounds.** No code change; four requests at most; one model, one server. Branch `feature/004-tool-call` from
`main`; commit with the owner's identity and the usual tail; no push; deliver the branch and the SHA, then stop.
