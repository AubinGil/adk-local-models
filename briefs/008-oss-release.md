# Brief 008 — prepare the first public release and draft the Show and Tell

**Why.** Brief 007 settled what this package is: a lightweight, direct alternative for connecting Google ADK to
local OpenAI-compatible inference servers without LiteLLM or the OpenAI SDK, useful where errors as responses,
final-only tool calls, rejected truncated streams, documented per-profile knobs and attached request/reply hashes
are requirements, and not needed merely to reach a local server. The owner now wants the repository
`AubinGil/adk-local-models` made ready for a first public release on that description, plus a draft announcement
for the Google ADK Show and Tell. The owner's assignment arrived as a document on 2026-10-28; this brief is its
form for Codex. Baseline `f64919c` on `main`. Nothing here competes with ADK or LiteLLM; the deliverable is a
well-documented alternative and an honest account of what it does and does not do.

**Steps.**

1. **Documentation.** Rewrite `README.md` so that it states, in this order: what the package does; why it exists
   (the requirements above, not LiteLLM's history); how it differs from ADK's native
   `google.adk.integrations.openai.OpenAILlm`, both ways, drawn from the table in `briefs/007-result.md`; the
   supported servers (vLLM, Ollama, llama-server) and which were validated live (vLLM and Ollama; llama-server
   model-free only); installation and the minimal usage already shown; features and limitations; tested
   configurations with pointers to `runs/` for reproducibility. Use the narrowed description verbatim where the
   package is introduced. Remove the stale sentences that still describe brief 001 ("no owner's server was
   contacted", "no live compatibility claims are made before brief 002"). Make no claim that the adapter is
   faster, safer, better or more efficient than the native class; "lightweight" means the four transport
   packages (12.7 MiB in brief 007), not the ADK closure. Match `pyproject.toml`'s `description` to the README.
2. **Repository organisation.** Inventory everything tracked under `briefs/`, `runs/`, `tools/`, `tests/fixtures/`
   and the top level, and write a recommendation table (path, keep public / archive / exclude, reason) into the
   result file. Known items to assess: `AGENTS.md` carries the owner's email and a local Windows path in its
   Codex rules; `runs/007-native-compare/dependencies/project-pip-list.json` carries the editable-install path;
   the native comparison exchanges carry the inert `Bearer comparison-placeholder` header; the fake-server test
   uses `test-only-secret`. Say for each whether it is a problem for a public repository and what the remedy is.
   Delete nothing under `runs/` or `briefs/` and rewrite no history: the owner authorises removals separately.
   Keep brief 007 and its result reachable from the README as the supporting comparison.
3. **Security and privacy audit.** Scan every tracked file and the whole history (`git log -p`, all branches)
   for credentials, tokens, private keys, personal paths, host names, Tailscale addresses and private evaluation
   data; check `.gitignore` covers `.venv/`, `.cache/`, `runs/*/raw/`, build output and `*.egg-info/` (it does
   today; confirm nothing listed slipped in earlier). Report findings with the commit and path for each and a
   proposed remediation; apply nothing that rewrites history.
4. **Dependencies and licences.** From the project `.venv`, record the declared requirement (`google-adk>=2.13.0,<3`)
   and the installed closure; prove again that neither `litellm` nor `openai` is importable (the existing test
   covers `litellm`; add the `openai` check to the same test). List the licences of the closure as declared in
   metadata, flag anything that is not Apache/MIT/BSD-class, and confirm `LICENSE` is Apache-2.0 and matches
   `pyproject.toml`. Add no dependency.
5. **Reproducibility.** Create a fresh environment under `.cache/release-check/`, install the package from the
   working tree with `pip install -e .` and once from a built wheel (`pip wheel .` into that throwaway
   environment; install `build` there only if the owner allows), import it, run `python -m unittest discover -v`,
   and execute each README example against the in-process fake server from `tests/fake_server.py` with `base_url`
   pointed at it, so the examples are checked without a model. Record the commands and outputs in the result.
   Do not start, stop, reload, pull or modify any of the owner's servers; live evidence stays what `runs/` already
   holds, and the README keeps the model-free / live distinction visible.
6. **Feature documentation.** In the README, or a short `COMPARISON.md` the README links, present the brief 007
   comparison fairly: this package's features (direct integration through ADK's existing `httpx`; explicit vLLM,
   Ollama and llama-server profiles; streaming and function calling; tool calls only in the final streamed
   response; ADK error responses instead of raised SDK exceptions; truncated-stream detection; request/reply
   SHA-256; advertised server identity in `custom_metadata`) and its limitations (no image or audio parts; no live
   bidirectional API; no strict output-schema enforcement; no reasoning-token usage mapping; llama-server not
   validated live), and the native class's additional capabilities (image parts, strict response schema,
   reasoning-model handling and `thoughts_token_count`, Responses API sibling). Every row cites a test, a `runs/`
   folder or `briefs/007-result.md`.
7. **OSS readiness files.** Add concise `CONTRIBUTING.md` (how to set up, run tests, what a change needs: a
   model-free test, documented knobs cited to the vendor, no new dependency without discussion) and `SECURITY.md`
   (a private reporting route the owner fills in; scope: the adapter sends requests only where `base_url` points
   and never configures servers). Verify `LICENSE`, state supported Python (3.11+) and ADK (2.13.x tested, `<3`
   declared) in the README, and keep the examples runnable. No code of conduct, roadmap, changelog or governance
   file unless the owner asks; the release must not grow into a framework.
8. **Show and Tell draft.** Write `SHOW_AND_TELL_DRAFT.md`: introduce the adapter and its purpose; acknowledge
   ADK's native `OpenAILlm` as the default path for most users; explain the specific requirements that motivated
   this package; name the supported servers and what was verified live; summarise verified functionality with
   its evidence; one minimal example; the repository link; an invitation to test, report and contribute.
   Collaborative and factual. No criticism of LiteLLM, no suggestion that its users chose unsafely, no novelty or
   security claims beyond what the tests and `runs/` show. The owner submits it, or does not.
9. **Final gate and report.** Run the full test suite; check every README and `COMPARISON.md` example against the
   implementation; check every relative link resolves; confirm licence and dependency declarations; re-read the
   public-facing files for sensitive information; confirm each public claim has a test, a `runs/` record or a
   brief behind it. Write `briefs/008-result.md` with: files changed; test results; security and dependency
   findings with proposed remediations; known limitations; remaining release blockers that need the owner's
   decision; the Show and Tell draft's location; `git status` and the commit SHA.

**Bounds.** Core behaviour of `OpenAICompatibleLlm` unchanged except the `openai` import check in the existing
isolation test; no new dependency; `litellm` and the OpenAI SDK never installed in the project environment. No
deletion under `runs/` or `briefs/`, no history rewrite, no `.gitignore` change that hides tracked evidence. The
repository stays private, no release or package is published, the announcement is not submitted, harness-core is
untouched, no new research track. Branch `feature/008-oss-release` from `main`; commit with the owner's identity
and the usual tail; no push; deliver the branch and the SHA, then stop. The owner decides whether to publish.
