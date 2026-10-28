# adk-local-models — start here

A Google ADK model adapter for local OpenAI-compatible servers (vLLM, Ollama, llama-server) that never goes
through LiteLLM. Parked side project of the owner (2026-10-28); harness-core stays the main track. Codex executes
the briefs in `briefs/`; the reviewer (Fable) writes them and gates; the owner types "go".

**No open assignment for Codex (2026-10-28, after brief 008's gate).** The release candidate is on `main`: README,
`COMPARISON.md`, `CONTRIBUTING.md`, `SECURITY.md`, `SHOW_AND_TELL_DRAFT.md` and recorded checks under
`runs/008-release-check/`. Three decisions are the owner's before publishing, with the reviewer's recommendations in
`briefs/008-result.md`: the private security route, the two transitive licences (certifi MPL-2.0, typing_extensions
PSF-2.0, recommended accept), and disclosure (recommended: keep briefs and runs, edit this file's path and e-mail
lines). The narrowed description from brief 007 stands: a lightweight, direct alternative for connecting Google ADK
to local OpenAI-compatible servers without LiteLLM or the OpenAI SDK, useful where errors as responses, final-only
tool calls, rejected truncated streams, documented knobs and attached request/reply hashes are requirements, and not
needed merely to reach a local server. The owner writes or submits any public post.

**Release scope (owner's decision, 2026-10-28):** a v0.1.0 public GitHub release only, no PyPI publication, no release
automation and no governance files. The bar is that another developer can find the repository, understand its
trade-offs, install it in a clean environment and reproduce its basic behaviour. The announcement text in
`SHOW_AND_TELL_DRAFT.md` is the owner's, checked claim by claim against the evidence at the brief 008 gate.

## Why this exists

- ADK (Apache-2.0, Python/Java/Go/TS) runs locally; only Gemini is a native model class. Every other model,
  including vLLM and Ollama, is routed through the `LiteLlm` wrapper, which rewrites requests, pulls in a very
  large dependency tree, and was compromised on PyPI twice in 2026 (1.82.7/1.82.8 in March; 1.107.0 on
  October 21 with a credential stealer that ran at Python startup). LiteLLM is never installed here.
- **Correction (2026-10-28):** ADK does ship a native OpenAI-compatible class, `OpenAILlm` under
  `google.adk.integrations.openai` (out of labs since 2026-09-23, release v2.10.0), behind the `openai` extra, so it
  needs the OpenAI SDK; the Python documentation page still describes only LiteLLM, which is why it was missed. The
  package's remaining claim is narrower: no LiteLLM and no OpenAI SDK, exact request and reply bytes hashed, documented
  per-profile knobs only. Brief 007 tests whether that claim is worth a separate package.
- The owner's rules carry over from harness-core: request shapes come from vendor documentation, not invention;
  the exact bytes sent and received are recorded with hashes; shipped dependencies need Apache/MIT-class licenses;
  the model servers are the owner's (check, never start, stop, pull or reload without the owner's word).

## The design (fixed; refine in briefs, do not replace)

One class, `OpenAICompatibleLlm(BaseLlm)`, in package `adk_local_models`, with a `profile` of `vllm`, `ollama` or
`llama_server`, a `base_url`, a `model`, an optional `api_key`, an `extra_body` dict and a timeout. It implements
`generate_content_async(llm_request, stream=False)` as ADK's `BaseLlm` requires: with `stream=False` exactly one
`LlmResponse` with `partial=False`; with `stream=True` partial chunks with `partial=True` and a final chunk with
`partial=False` that equals the non-streamed output. Tool calls are emitted only in the final chunk. It declares
`capabilities` as a plain property and `supported_models()` as the three prefixes `vllm/`, `ollama/`,
`llama-server/` for `LLMRegistry`. `connect()` stays unimplemented (no live API).

Mapping, both directions, from ADK's Gemini-shaped request to chat completions:
`config.system_instruction` to the system message; `contents` roles `user`/`model` to `user`/`assistant`; a
`function_call` part to an assistant `tool_calls` entry; a `function_response` part to a `tool` message with the
matching `tool_call_id`; `config.tools[*].function_declarations` to `tools` of type `function`, with the Gemini
schema converted to JSON schema; `temperature`, `top_p`, `max_output_tokens`, `stop_sequences` and a JSON
`response_mime_type` to their chat-completions names; the reply's `tool_calls` back to `function_call` parts with
the ids kept so the next turn can answer them; `finish_reason` and `usage` mapped; HTTP and transport failures
returned as `LlmResponse(error_code, error_message)`, not raised. Every response carries in `custom_metadata` the
SHA-256 of the exact request body and of the raw reply, the server identity read once from `/v1/models`, and the
profile. The three profiles differ only in documented knobs (vLLM: chat-template arguments for thinking; Ollama:
keep-alive and the think switch; llama-server: its reasoning-format and tool-template requirements), each cited
to the vendor's documentation in the code.

## Rules for Codex here

- Branch from `main`, commit with `git -c user.name="Aubin" -c user.email="gildas.tien@gmail.com"`, end every
  commit message with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`, never push, deliver the SHA
  and stop. `.venv/` and `.cache/` never committed; no `git add -A`.
- Dependencies: `google-adk` and what it already pulls in; nothing else without the brief saying so; `litellm`
  never, and a test proves it is not importable in the project's environment.
- Model-free first: every behaviour proven against an in-process fake OpenAI-compatible server with recorded
  fixtures. Live calls to the owner's servers only in a brief that says so, with the owner's word, and the
  readings written into a file under `runs/`.
- Do not touch `C:\Users\aubin\harness-core`; this package stands alone (the request-recording idea is borrowed
  from harness-core's `VLLMProvider`/`ServingContract`, not imported).
