# Brief 004 readings

One identity GET and four sequential completions against only
`http://localhost:8038/v1`, model `nemotron-3.5-bolt-e4b`, on 2026-10-28
15:09:54-15:09:57 UTC. No retries, server changes, tool execution, or code changes.

Each completion starts with a deep copy of `tests/requests.py`'s tool fixture,
with `config.response_mime_type=None`. This removes `response_format`. All other
fixture settings remain: tools, instructions, temperature 0, top_p 0.9,
max_tokens 32, and stop sequence END. `omitted-*` has no `tool_choice`;
`required-*` adds `tool_choice="required"` via the adapter's existing `extra_body`.
Both variants use `chat_template_kwargs.enable_thinking=false`, as in brief 003.

Sources read for these settings:

- [vLLM 0.31.0 tool calling, Required Function Calling](https://docs.vllm.ai/en/v0.31.0/features/tool_calling/#required-function-calling), read 2026-10-28.
- [NVIDIA model card, Reasoning Off](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16), checked in brief 003.

`summary.json` records identity, versions, sources and outcomes. Each exchange
directory contains exact `request.bin` / `reply.bin` entities and `exchange.json`
with method, URL, response status/headers, wall time, lengths and SHA-256 values.
Completion records include all adapter responses; `custom_metadata.json` also
stores each yielded metadata object separately. SSE framing is included in reply
hashes; HTTP headers and transfer framing are excluded. The local attributes
preserve `.bin` files without newline conversion.

The unchanged adapter performed all calls. A temporary observer wrapped httpx
send/raw-read methods only to retain bytes and timing, without replacing transport
or transforming requests. The adapter's identity read was made once explicitly
with a 3-second timeout, then its cached identity was reused for completions
(120-second per-operation timeout). No credentials or environment proxies used.

`verification.json` records offline byte/hash, metadata, request-shape, raw-tool-ID
and argument checks, partial-stream prefix hashes, and pair comparisons after
normalizing distinct server-generated tool IDs. No additional live calls were
made for verification. See [the result](../../briefs/004-result.md).
