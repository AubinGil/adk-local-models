# Brief 003 readings

Actual sequential exchanges with `http://localhost:8038/v1` on 2026-10-28,
14:58:22-14:58:26 UTC. One adapter identity read, followed by exactly four
completions: fixture text and tools requests, each plain and streamed. No retry,
other local endpoint, server lifecycle action, tool execution or code change.

`summary.json` contains versions, source commit, wall times, identity, request
outcome checks and the thinking-control source. Each exchange directory contains
`request.bin` and `reply.bin` (exact HTTP entity bytes), plus `exchange.json`
(URL/method, status, response headers, timings, lengths, SHA-256 and, for
completions, every serialized adapter response). Completion directories also
contain `custom_metadata.json`, recording each yielded response's metadata.
Probe GET request entity bytes are empty. HTTP headers/transfer framing are not
part of entity hashes; SSE framing is. `.bin` attributes prevent newline changes.

The unchanged adapter performed all HTTP calls. A temporary observer wrapped
httpx send/raw-read methods to retain bytes and timing, without transforming
requests, replacing transport, or adding retries. Identity was read explicitly
through the adapter's `_read_identity` with a 3-second timeout, then reused from
that instance's cache for all four completions (120-second per-operation timeout).
Requests used no credentials, ignored environment proxies, and requested identity
content encoding. The fixture `max_tokens=32`, JSON response format, sampling,
stop sequence, instructions and tool declaration were preserved.

Thinking control comes from NVIDIA's model card, **API Client / Reasoning Off**:
https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16
(read 2026-10-28). All four requests use
`chat_template_kwargs={"enable_thinking":false}`. No other model-card generation
settings were added. HTTP acceptance and reported zero reasoning tokens were
observed; hidden server/template configuration was not inspected.

`verification.json` records offline verification of hashes, lengths, fixture
request shapes, metadata, partial reply-prefix hashes and semantic equality of
plain/streamed final responses. These checks send no additional requests.
See [the result](../../briefs/003-result.md) for limits and follow-up findings.
