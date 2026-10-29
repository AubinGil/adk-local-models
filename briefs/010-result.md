# Brief 010 result: keep raw-text knob; reject its JSON combination

Four isolated completions, all without JSON mode, returned HTTP 200 on LFM3-1.7B Q4_K_M under llama.cpp 0.8.0, tag b11960. Two identity reads; no retries. The two servers were stopped by PID and the final process reading was empty.

| Server setting | Request knob | HTTP / finish | Observation at 32 tokens |
|---|---|---|---|
| --reasoning off | None | 200 / length | Answer text, no reasoning_content |
| --reasoning off | reasoning_format none | 200 / length | Raw content starts with empty think tags, then answer text |
| Default reasoning | None | 200 / length | Empty answer; reasoning_content populated |
| Default reasoning | reasoning_format none | 200 / length | Raw content starts with think tag and reasoning; no separate reasoning_content |

The [pinned README](https://github.com/ggml-org/llama.cpp/blob/b11960/tools/server/README.md), chat-completions options, states:

> The reasoning format to be parsed. If set to `none`, it will output the raw generated text.

The CLI section distinguishes --reasoning (on/off/auto) from --reasoning-format, which controls parsing/extraction of thoughts. Thus none changes output formatting, not whether the model thinks. The isolated observations match that meaning. Combined with brief 009's recorded HTTP 400 on JSON mode plus none, this selects the first prescribed fix, without claiming a server-side root cause.

`profiles.py` now rejects llama_server reasoning_format none with mapped json_object response mode before the identity GET or completion POST, yielding INVALID_REQUEST. Other profile behavior is unchanged. The knob remains available without JSON mode. The JSON text golden now omits this knob; tools/history goldens retain it. The new model-free test covers both stream modes, zero server contact on rejection, and success with the knob alone. README documents the restriction and links both live runs.

README, COMPARISON and SHOW_AND_TELL_DRAFT now state the narrow live evidence from brief 009: one model, LFM3-1.7B Q4_K_M, llama.cpp 0.8.0 b11960, --jinja --reasoning off, including both Runner round trips. pyproject.toml is 0.1.1 for the owner to tag; published 0.1.0 release notes remain untouched.

Validation: 18 model-free tests pass (the prior 17 plus one), including absence of LiteLLM and OpenAI SDK. All twelve recorded entity hashes and completion metadata hashes verify offline. Git diff checks pass; committed raw blobs checked against hashes. No push, tag, release or public post.

Final `pgrep -af "[l]lama-server"`: no output. Both started server PIDs (90653, 90711) and the workstation SSH tunnel were stopped. Ollama resident-model list stayed empty; final available memory 5142 MB. No unrelated service changes.

[Readings](../runs/010-llama-server-knob/README.md), [summary](../runs/010-llama-server-knob/summary.json), [verification](../runs/010-llama-server-knob/verification.json).
