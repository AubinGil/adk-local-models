# Brief 007 — compare with ADK's own `OpenAILlm`

**Why.** ADK ships a native OpenAI-compatible model class, `google.adk.integrations.openai.OpenAILlm`, since the
commit of 2026-09-23 that moved it out of labs (first release v2.10.0, 2026-09-25). It needs the OpenAI SDK
(`google-adk[openai]`, `openai>=2.20,<3`), is imported lazily, takes `base_url` and `api_key` for any
OpenAI-compatible host, maps tools, streams with tool-delta accumulation, sends `reasoning_effort` for models it
recognises as reasoning models by name, supports structured output and image parts, and has a Responses API
sibling. The Python documentation page for OpenAI still describes only the LiteLLM path, which is why it was
missed. The question for this package is now plain: what does `OpenAICompatibleLlm` do that `OpenAILlm` plus a
recording HTTP client would not, and is that worth a separate package?

**Steps.**
1. A separate environment under `.cache/native-compare/` with `google-adk[openai]`; the project's own `.venv`
   stays without the OpenAI SDK so the gated test that `litellm` is absent and the dependency claim stay true.
   Record `pip list` sizes and the dependency closure of each environment.
2. Model-free: run the three fixed requests through both classes against the fake server, capturing the exact
   bytes `OpenAILlm` sends by giving it a pre-configured `AsyncOpenAI` whose `httpx` client has event hooks.
   Diff the wire bodies field by field (message shapes, tool schema conversion, tool_choice default, max tokens
   field, response format, stream options, extra headers), and the responses (finish reasons, usage, reasoning
   token count, partial semantics, error behaviour on HTTP 500, malformed JSON, truncated SSE, connection
   refused).
3. Live, on the owner's word, against the same servers used in briefs 003 to 006 that are up: text and tool
   requests, plain and streamed, and one `Runner` round trip, through `OpenAILlm` with `base_url` set; the same
   readings layout as before under `runs/007-native-compare/`.
4. `briefs/007-result.md`: one comparison table (feature, `OpenAILlm`, `OpenAICompatibleLlm`, evidence), the
   dependency table, the wire diffs, and a recommendation with its reasoning: keep the package with a narrowed
   description, reduce it to a recording transport around the native class, or retire it. The recommendation is
   Codex's; the owner decides. The description proposed by the owner's correspondent, "a lightweight, direct
   alternative for connecting Google ADK to local OpenAI-compatible servers, without LiteLLM or the OpenAI SDK",
   is tested against the evidence, not assumed.

**Bounds.** No change to the package in this brief; at most twelve live requests per server; nothing pulled or
started. Branch `feature/007-native-comparison` from `main`; the owner's identity and the usual tail; no push;
deliver the branch and the SHA, then stop. Any public post about the package is written and submitted by the
owner.
