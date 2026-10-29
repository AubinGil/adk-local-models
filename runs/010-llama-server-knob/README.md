# Brief 010: isolated reasoning format checks

Authorized by the owner's go on 2026-10-28. Source main 8ed5589; branch feature/010-llama-server-knob.
Server/model: llama.cpp 0.8.0 (b11960, commit 8642541), LFM3-1.7B Q4_K_M, alias lfm3-1.7b.
SSH to gildas01@100.126.229.13; local tunnel 8111:127.0.0.1:8111; adapter base http://127.0.0.1:8111/v1.

## Preconditions and cleanup

| Reading | Before | After |
|---|---|---|
| pgrep -af llama-server (self-excluding pattern) | Empty | Empty |
| ollama ps | Empty | Empty |
| free -m available | 5146 MB | 5142 MB |

First server PID 90653, second PID 90711. Both detached using nohup with stdin /dev/null and log ~/lfm3-tests/009-server.log, as brief 009 specifies. First command:

```
PATH=/usr/local/cuda/bin:$PATH ~/llama.cpp-lfm3/build/bin/llama-server -m ~/models/lfm3/LFM3-1.7B-Q4_K_M.gguf -a lfm3-1.7b --host 127.0.0.1 --port 8111 -c 4096 -np 1 -ngl 99 --no-warmup --jinja --reasoning off
```

Second command is identical with `--reasoning off` removed. Health returned ok before each pair. Each server was stopped by its own PID, and the workstation tunnel was stopped. Final `pgrep -af "[l]lama-server"` returned no output. Nothing unrelated started/stopped/installed/pulled.

## Requests and recording

Exactly four completion POSTs and two identity GETs, no retries or extra diagnostic completions. The unmodified adapter at capture time sent the fixed text request with response_mime_type cleared (no response_format); model alias and stream false as recorded. Same 32-token limit, temperature 0, top_p 0.9 and END stop. Each pair: no knob, then reasoning_format none. Identity cached once per server run.

Temporary observers of httpx send/raw-read and adapter output saved exact request/reply entities and metadata without transforming requests. Every exchange has request.bin, reply.bin and exchange.json; completions have custom_metadata.json. Hashes exclude headers/HTTP transfer framing. The run-local .gitattributes preserves raw bytes. Offline verification recomputed all entity and adapter metadata hashes, checked no request contains response_format, and confirmed all six HTTP statuses are 200. See summary.json for raw answer/reasoning text, usage and timings; verification.json records checks.

Both knob requests succeed without JSON mode. Prior HTTP 400 evidence is in ../009-llama-server/knob-off/text-none/ and ../009-llama-server/knob-default/text-none/. The package now rejects that combination before I/O, while preserving the knob alone. No assertion about other server builds/models. No answer quality evaluation.

Source read: [llama.cpp b11960 server README](https://github.com/ggml-org/llama.cpp/blob/b11960/tools/server/README.md), chat-completions options and CLI reasoning controls. See [result](../../briefs/010-result.md).
