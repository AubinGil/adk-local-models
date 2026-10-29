# Brief 009 live readings

Authorized by the owner's go on 2026-10-28. Branch feature/009-llama-server-live from main fa71120.
Profile llama_server, model lfm3-1.7b, workstation API http://127.0.0.1:8111/v1 through SSH local forwarding to gildas01@100.126.229.13.

## Lifecycle and preconditions

| Reading | Before | After |
|---|---|---|
| llama-server process | None | None |
| ollama ps | Empty | Empty |
| Available RAM (free -m) | 5022 MB | 5128 MB |

An initial pgrep -af pattern also matched the SSH command carrying the version command; pgrep -ax llama-server confirmed no actual server before starting. No unrelated process was stopped.
Binary version: 0.8.0-dev (build 1, commit 8642541), GNU 13.3.0 Linux aarch64. This differs from the brief's b11960 description; evidence applies to the actual binary only.

First server PID 90256, detached with stdin /dev/null and output ~/lfm3-tests/009-server.log:

```
PATH=/usr/local/cuda/bin:$PATH ~/llama.cpp-lfm3/build/bin/llama-server -m ~/models/lfm3/LFM3-1.7B-Q4_K_M.gguf -a lfm3-1.7b --host 127.0.0.1 --port 8111 -c 4096 -np 1 -ngl 99 --no-warmup --jinja --reasoning off
```

Second server PID 90300, same detachment/log:

```
PATH=/usr/local/cuda/bin:$PATH ~/llama.cpp-lfm3/build/bin/llama-server -m ~/models/lfm3/LFM3-1.7B-Q4_K_M.gguf -a lfm3-1.7b --host 127.0.0.1 --port 8111 -c 4096 -np 1 -ngl 99 --no-warmup --jinja
```

Health returned loading then ok for first server and ok for second. Both servers were stopped by their recorded PIDs; final pgrep -ax llama-server returned no output. SSH tunnel workstation PID 30512 was stopped. No install, pull, unrelated service change, or sibling repository access.

## Capture method

13 API exchanges: two identity GETs, eleven completion POSTs. Four fixture POSTs, four Runner POSTs, three knob POSTs. No completion retries. Health and SSH readings are separate readiness/lifecycle checks. Bounds: at most 16 completions and three identity reads.

The current fixed_requests text/tools fixtures were used without extra_body for smoke. Runner uses the brief 005 instruction and deterministic weather function, fresh sessions, temperature 0, top_p 0.9, max_output_tokens 128, max_llm_calls 2, NONE/SSE respectively. Each tool executed once and returned temperature 20.
Temporary httpx send/raw-read and adapter-generator observers recorded exact entity bytes without changing transport or request mapping. Every exchange contains request.bin, reply.bin, exchange.json; completions also contain custom_metadata.json. Runner sessions and yielded events are saved. Metadata partial hashes were checked against prefixes of captured SSE bytes; final hashes against full bytes. No credentials supplied. The capture scripts remain in ignored .cache; package code is unchanged.

See summary.json, verification.json and ../../briefs/009-result.md. Both knob requests failed HTTP 400, so public surfaces/version remain unchanged under the conservative failure rule. No inference that the knob is universally unsupported: JSON mode and a 32-token cap are part of this exact fixture.
