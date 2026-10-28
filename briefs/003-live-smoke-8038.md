# Brief 003 — the live smoke against the owner's vLLM on 8038

**Goal.** Brief 002's smoke (`briefs/002-live-smoke.md`, steps 2 and 3, unchanged) against a server that answers.
The owner started it and offered it on 2026-10-28 ("ive got something on 8038 for you"); that is the word for
these calls. The server is the owner's: check, never start, stop or reload.

**The server, as read at the gate on 2026-10-28:** `http://localhost:8038/v1`, vLLM, model id
`nemotron-3.5-bolt-e4b` (NVIDIA Nemotron 3.5 Bolt E4B, BF16), `max_model_len` 16384, bound to localhost only.
Profile `vllm`, `base_url="http://localhost:8038/v1"`, `model="nemotron-3.5-bolt-e4b"`.

**Steps.**
1. Identity: the adapter's `/v1/models` read, recorded with its hash.
2. The thinking knob: read the model's card or chat template for the documented way to turn thinking off under
   vLLM (`chat_template_kwargs`); record the source; if nothing documented exists, send no knob and say so.
   Nothing is invented.
3. The four requests of brief 002 step 2: the fixtures' plain text request and the `weather` tool request, each
   once non-streamed and once streamed; no retries; one at a time. If the server rejects the tool request
   because tool calling is not enabled on its side, record the exact reply and stop that pair; do not change the
   server.
4. Readings under `runs/003-live-smoke-8038/`: exact request bytes, raw reply bytes, `custom_metadata`, wall time,
   whether a tool call came back parsed with a JSON-object argument.
5. `briefs/003-result.md`: the one table of brief 002 for this profile, every difference between the live replies
   and the fixtures' assumptions (field names, finish reasons, usage, reasoning fields, SSE framing), and what the
   adapter would need to change, recorded for a later brief and not fixed here.

**Bounds.** No code change; the 16 tests stay as gated. One server, one model, one request shape, no judgement of
answer quality. Branch `feature/003-live-smoke` from `main`; commit with the owner's identity and the usual tail;
no push; deliver the branch and the SHA, then stop.
