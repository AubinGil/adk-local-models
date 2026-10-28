# Brief 005 live Runner readings

Actual run on 2026-10-28, 15:59:54-15:59:57 UTC, against only
`http://localhost:8038/v1`, `nemotron-3.5-bolt-e4b`. One identity GET reused by
both turns, then two completion POSTs per turn: **five HTTP requests total**.
No retries, server changes, other endpoints, or external weather service.

Each turn used a fresh `InMemorySessionService`, an `LlmAgent` named `local`,
and `Runner.run_async`. The session IDs are `plain` and `stream`, app name
`adapter_smoke_005`, user `user`. User message: `Weather in Paris?`.
Instruction: `Be concise. Use weather once for the requested city, then answer
from its result. Do not call weather again after receiving its result.`
ADK appended its internal-name instruction; actual system messages are recorded.

Run-specific generation config was temperature 0, top_p 0.9, max_output_tokens
128, no JSON mime type and no stop sequence. This is a Runner smoke rather than
another 32-token fixture replay. No `tool_choice` was supplied. Thinking was
disabled through `chat_template_kwargs.enable_thinking=false`, documented in the
[NVIDIA model card, Reasoning Off](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16)
and already checked in brief 003.

The tool was a local deterministic function with this behavior:

```python
def weather(city: str) -> dict:
    """Get weather for a city."""
    # The observer additionally logs city and result without changing the result.
    return {"temperature": 20}
```

RunConfig used `StreamingMode.NONE` then `StreamingMode.SSE`, each with
`max_llm_calls=2`. A separate observer capped all attempted HTTP sends at six and
restricted URLs to this server's models and chat-completions routes. Neither
limit was reached. The adapter timeout was 120 seconds per operation; the
explicit adapter identity read used 3 seconds. No credentials or environment
proxies were used.

The adapter and transport were unchanged. Temporary observers wrapped httpx
send/raw reads and the adapter generator to retain exact bytes and responses;
they added no request rewrite, retry, or replacement transport. Per-completion
wall time includes yielding responses to Runner. Each exchange contains:

- `request.bin`, `reply.bin`: exact HTTP entities; SSE framing included, HTTP
  headers and transfer framing excluded. `.bin` attributes prevent conversion.
- `exchange.json`: URL/method, status/headers, times, lengths, hashes, the ADK
  request, and all adapter responses. The probe contains identity instead.
- `custom_metadata.json` for completions: metadata for every yielded response.

Each turn additionally contains `tool_executions.json`, `yielded_events.json`
(all Runner output events including partials), and `session_events.json`
(persisted user, call, function-response and final-answer events). `summary.json`
records outcomes and total HTTP count. `verification.json` records offline checks
of every hash, ID linkage, once-only execution and final session text. Those
checks sent no further requests. See [the result](../../briefs/005-result.md).
