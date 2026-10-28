# Brief 001 delivery

Implemented on `feature/001-adapter`, based on `main`. All adapter HTTP calls in
verification use the in-process loopback fake server; no owner's server was
checked, started, stopped, pulled, or reloaded. No harness-core files were read
or changed. No push is part of this brief.

Includes pure mapping functions, async transport, documented profiles, byte
hashes and cached identity, synthetic replay fixtures, nine fixed wire goldens,
and an ADK Runner / session / function-tool round trip. Tests use no added test
dependencies and assert LiteLLM is not importable.

Design issues for Fable / the next brief:

- Ollama's documented `/v1/chat/completions` uses `reasoning_effort` or
  `reasoning.effort` for thinking control. `keep_alive` and native `think` cannot
  be assumed to work there. These two fields are rejected rather than inventing
  a shape or adding native transport. Native support remains deferred.
  Sources: https://docs.ollama.com/api/openai-compatibility and
  https://docs.ollama.com/api/chat .
- Literal equality of streamed and plain responses conflicts with recording
  their exact different requests/replies. Final content, partial flag, finish
  reason and usage are equal; `custom_metadata` differs. Partial hashes cover
  received prefixes, explicitly flagged as incomplete. Reconsider in a later brief.
- ADK 2.13 uses regex **fullmatch**, so the prefix patterns must be `vllm/.+`,
  `ollama/.+`, `llama-server/.+`. Construction strips the prefix; no new profile.
- `/v1/models` cannot guarantee implementation/version. Identity stores the
  advertised listing, exact raw hash and Server header. Failed probes are cached
  once as an error marker rather than blocking all completions.
- ADK exposes `LlmCapabilities` via internal `_capabilities` in 2.13.0. The plain
  property uses that type and declines output-schema-plus-tools enforcement.
  Later ADK compatibility needs verification; the dependency is bounded below 3.

Dependency license review (installed distribution metadata, ADK 2.13.0): this
package is Apache-2.0 and declares only google-adk. Imported dependencies are
google-adk / google-genai (Apache-2.0), httpx (BSD-3-Clause) and pydantic (MIT).
ADK's transitive environment contains **certifi 2026.10.23 (MPL-2.0)** and
typing_extensions 4.16.0 (PSF-2.0). Remaining installed runtime distribution
metadata reports Apache, MIT or BSD variants. This does not certify bundled
native-code licenses. No dependency wheels are vendored or shipped here.
The strict Apache/MIT-class rule cannot be claimed for the entire ADK closure
because of certifi; resolving this policy conflict is left for review without
substituting dependencies or weakening the rule in this brief.

Verification: Python 3.11.9, google-adk 2.13.0, google-genai 2.33.0, httpx 0.28.1.
All 16 unittest tests passed (including nine profile/request golden comparisons),
`pip check` passed, and `git diff --check` passed. Editable installation succeeded;
all three ten-line README examples were syntax checked without executing them.
Run `.venv\Scripts\python -m unittest discover -v` after installing the package.
Fixtures are authored synthetic protocol examples, not real-model captures.
See `tests/fixtures/README.md` for provenance and the byte contract.
