# Brief 001 — the model-free adapter

**Goal.** `adk_local_models.OpenAICompatibleLlm`, the class described in `AGENTS.md`, proven without any model.

**Deliver.**
1. `pyproject.toml` (package `adk_local_models`, Apache-2.0, Python 3.11+, dependency `google-adk` only),
   `src/adk_local_models/__init__.py`, `llm.py` (the class), `mapping.py` (request and response conversion as
   pure functions, so they can be tested without a server), `profiles.py` (the three profiles, each knob with a
   comment citing the vendor page it comes from), `recording.py` (hashes and server identity).
2. `tests/fake_server.py`: an in-process HTTP server speaking `/v1/models` and `/v1/chat/completions`, replaying
   fixtures from `tests/fixtures/` for both plain and streamed (SSE) replies, recording every request body it
   receives.
3. Tests, all model-free:
   - golden request bodies: for three fixed `LlmRequest`s (text only; with tools; with a prior function call and
     its response) the exact JSON sent per profile, compared to a committed golden file, so a shape change is a
     visible diff;
   - non-streamed text reply, non-streamed tool call reply, streamed text, streamed tool call (chunks partial,
     final chunk equal to the non-streamed output, tool calls only in the final chunk);
   - error mapping: HTTP 500, connection refused, malformed JSON, each returned as an `LlmResponse` with
     `error_code` and `error_message`, nothing raised;
   - the recording: `custom_metadata` carries request and reply SHA-256 that match the fake server's log;
   - one end-to-end turn through ADK itself: an `LlmAgent` with one function tool, run with `Runner` and
     `InMemorySessionService` against the fake server, where the fixture replies first with a tool call and then
     with a final answer, and the test asserts the tool ran once with the mapped arguments and the final text
     reached the session;
   - `litellm` is not importable in the environment.
4. `README.md` at the root: install, a ten-line usage example per profile, and what is not covered (no live API,
   no images, no structured-output enforcement beyond the JSON mime type).

**Bounds.** No live server call. No change to the design in `AGENTS.md`; a design problem found while
implementing is written into the delivery note and left for the next brief. Commit on `feature/001-adapter`,
`git diff --check`, deliver the branch and the SHA, then stop.

**Queued for 002, not now:** a live smoke against the owner's servers, one request per profile, with the owner's
word, readings under `runs/`.
