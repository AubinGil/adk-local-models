# Briefs

| # | Title | Status |
|---|---|---|
| 001 | The model-free adapter (`OpenAICompatibleLlm`, fake server, golden request bodies, ADK end-to-end turn) | delivered c5798de, gated 2026-10-28 within bounds (`001-delivery.md`) |
| 002 | Live smoke: all four configured endpoints unreachable, zero completion requests, readings under `runs/002-live-smoke/` | delivered 531a271, gated 2026-10-28 as a record of absence (`002-result.md`) |
| 003 | The same smoke as 002, run once the owner has a listed server up (Ollama `gemma4:12b`, a vLLM port, or a chat-capable llama-server) | superseded by 003 |
| 003 | The same smoke against the owner's vLLM on localhost:8038 (`nemotron-3.5-bolt-e4b`, 16k context), offered 2026-10-28 | delivered 770e227, gated 2026-10-28 within bounds: text and streaming hold live, no tool call because the request carried JSON mode (`003-result.md`) |
| 004 | The tool request on 8038 without JSON mode, then with the documented required tool choice; at most four requests | delivered e80c037, gated 2026-10-28: four parsed tool calls with ids, JSON mode was the cause (`004-result.md`) |
| 005 | The fixture split and a live `Runner` round trip on 8038, non-streamed and streamed | delivered 35b636e, gated 2026-10-28: 17 tests, both round trips complete with ids preserved (`005-result.md`) |
| 006 | The `ollama` profile live against the owner's main Ollama (`gemma4:12b`): identity, thinking knob, text and tool requests, a `Runner` round trip | delivered c534f31 on `gemma4:e4b` (12b absent, owner's word), gated 2026-10-28: ten exchanges verified, both round trips complete (`006-result.md`) |
| 007 | Comparison with ADK's native `OpenAILlm` (OpenAI SDK) on the same fixtures and servers; recommend keep, reduce or retire | delivered c7c9545, gated 2026-10-28: 300 wire files verified, both classes live on Ollama and vLLM; recommendation keep, narrowed (`007-result.md`); the owner decides |
| 008 | First public release preparation: README rewrite to the narrowed description, repository inventory, security and dependency audit, clean-environment reproduction, `CONTRIBUTING.md`/`SECURITY.md`, `SHOW_AND_TELL_DRAFT.md`; no publishing | written 2026-10-28, awaiting the owner's "go" |
