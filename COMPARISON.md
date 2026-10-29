# Comparison with ADK OpenAILlm

The [full comparison and its scope](briefs/007-result.md) records the experiments. Native capabilities marked source review were not exercised in that comparison.

| Capability | This adapter | Native OpenAILlm | Evidence |
| --- | --- | --- | --- |
| Transport | ADK's existing httpx; no OpenAI SDK | OpenAI SDK | [Dependency measurements](briefs/007-result.md) |
| Profiles | vLLM, Ollama, llama-server with documented knob validation | No generic extra_body property | [Profiles](src/adk_local_models/profiles.py), [comparison](briefs/007-result.md) |
| Text, streaming, functions | Supported; streamed tool calls only in final | Supported; tool calls may appear in partials | [Tests](tests/test_adapter.py), [comparison](briefs/007-result.md) |
| Errors and truncated streams | Errors returned as ADK responses; truncated streams rejected | SDK exceptions; observed truncated stream accepted | [Comparison](briefs/007-result.md) |
| Request/reply hashes and advertised identity | Attached in metadata | Not attached by class; configurable client can capture bytes | [Comparison](briefs/007-result.md) |
| Image and audio | Unsupported | Image parts supported | [Comparison](briefs/007-result.md), [tests](tests/test_adapter.py) |
| Strict output schema | Not enforced | Supported (source review) | [Comparison](briefs/007-result.md) |
| Reasoning | No reasoning-token usage mapping | Reasoning handling and thoughts_token_count | [Comparison](briefs/007-result.md) |
| Live bidirectional API | Not implemented | Responses API sibling available | [Comparison](briefs/007-result.md) |
| Server evidence | vLLM and Ollama live; llama-server live on LFM3-1.7B Q4_K_M, llama.cpp 0.8.0 (b11960), `--jinja --reasoning off` ([run](runs/009-llama-server/)) | Same comparison scope | [Live results](runs/007-native-compare/live/), [comparison](briefs/007-result.md) |
