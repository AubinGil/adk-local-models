# Briefs

| # | Title | Status |
|---|---|---|
| 001 | The model-free adapter (`OpenAICompatibleLlm`, fake server, golden request bodies, ADK end-to-end turn) | delivered c5798de, gated 2026-10-28 within bounds (`001-delivery.md`) |
| 002 | Live smoke: all four configured endpoints unreachable, zero completion requests, readings under `runs/002-live-smoke/` | delivered 531a271, gated 2026-10-28 as a record of absence (`002-result.md`) |
| 003 | The same smoke as 002, run once the owner has a listed server up (Ollama `gemma4:12b`, a vLLM port, or a chat-capable llama-server) | superseded by 003 |
| 003 | The same smoke against the owner's vLLM on localhost:8038 (`nemotron-3.5-bolt-e4b`, 16k context), offered 2026-10-28 | delivered 770e227, gated 2026-10-28 within bounds: text and streaming hold live, no tool call because the request carried JSON mode (`003-result.md`) |
| 004 | The tool request on 8038 without JSON mode, then with the documented required tool choice; at most four requests | written 2026-10-28, not started |
