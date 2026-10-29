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

## Gate (reviewer, 2026-10-28, at eccdc0f): accepted within bounds; 0.1.1 ready to tag

Reproduced on the branch: 18 tests pass; `git diff --check` clean; all 12 entity hashes of the four completions and
two identity reads recomputed and matching; every relative link in the public files and both run READMEs resolves;
the four examples run against the fake server, including the llama-server example that keeps the knob; no
comparative claim appears. The Jetson was left as found: no llama-server process, port 8111 closed, Ollama idle.

**The finding, read against the records.** Without JSON mode the knob behaves as llama-server's pinned README
says: `reasoning_format: none` leaves the think tags in the raw content and suppresses the separate
`reasoning_content`; it does not stop the model thinking. With `--reasoning off` the raw content opens with an
empty think pair and then the answer. So the knob is a formatting switch, the 400 of brief 009 belongs to its
combination with `response_format: json_object`, and the fix chosen is the right one of the two the brief allowed:
keep the knob, refuse the combination for the `llama_server` profile before any network I/O with
`INVALID_REQUEST`, test both stream modes for zero server contact on rejection and for the knob passing through
alone. The guard reads the mapped body, so it fires on `response_mime_type="application/json"` and nothing else.
The golden fixture for the llama-server JSON text request now omits the knob, which is what the adapter sends.

**Public surfaces.** README, `COMPARISON.md` and the draft now state the live evidence narrowly: one model,
LFM3-1.7B Q4_K_M, llama.cpp 0.8.0 tag b11960, `--jinja --reasoning off`, pointing at `runs/009-llama-server/`.
The README's llama-server paragraph states the knob rule and cites both runs and the pinned server documentation.
`pyproject.toml` is 0.1.1; the 0.1.0 release notes are untouched, as briefed.

**Bounds.** One model and one server build; the server-side cause of the sampler error is not established and
the README does not claim it. The owner tags 0.1.1 and writes the release notes.

