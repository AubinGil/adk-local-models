# Brief 006: reachable Ollama, required model absent

One actual adapter `GET http://127.0.0.1:11434/v1/models` was performed on
2026-10-28 at 16:22:16 UTC. It succeeded, but `gemma4:12b` was not listed.
No completion, native API, Runner, model pull, retry, or other endpoint call was
made. In particular, port 11435 and cloud models were not used.

The check began under the owner's direct instruction, `go ollama is available`,
using brief 002's existing Ollama endpoint/model. The owner then supplied brief
006, which explicitly requires stopping when that model is absent. The existing
reading was retained rather than repeating the GET. Its folder was moved from
the preliminary `runs/006-ollama-smoke/` to the required `runs/006-ollama/`.
The original summary's source commit and authorization describe capture time;
its follow-up annotation records the updated brief and final disposition.

`ollama/probe-1/request.bin` is the empty GET entity. `reply.bin` is the exact raw
models response. `exchange.json` records attempted method/URL, response status
and headers, adapter identity, wall seconds, lengths and entity hashes. The
identity hash is the raw GET reply hash. HTTP headers and transfer framing are
excluded. `.bin` attributes prevent newline conversion. No credentials were used.

The adapter was unchanged. A temporary observer wrapped httpx send/raw-read
methods only to retain bytes/timing; the adapter's `_read_identity` performed the
request with a three-second timeout and cached the result. Environment proxies
were ignored. No request transformation, replacement transport, or retry.

`summary.json` records the listing, source commit, versions, selected model,
absence reason, and empty completion sample list. Its thinking-control field
records a planned setting, **not a transmitted or validated knob**. Model-specific
thinking checks were not reached. `verification.json` records offline checks of
the one captured exchange, model absence, and empty completion samples.

See [the result](../../briefs/006-result.md). The run proves reachability and model
absence at check time, not Ollama generation, streaming, tool or Runner support.
