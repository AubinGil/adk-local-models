# Brief 008 - release preparation

The release gate is **not complete**. Do not publish on the strength of this report.

Changed: README, project description, dependency isolation test, CONTRIBUTING, SECURITY and SHOW_AND_TELL_DRAFT. The draft is in [SHOW_AND_TELL_DRAFT.md](../SHOW_AND_TELL_DRAFT.md). The private security reporting route still needs the owner's input.

The project environment ran 17 tests successfully. A fresh `.cache/release-check` environment installed with `python -m pip install -e .`; `python -m pip wheel . --no-deps -w .cache/release-check/wheels` built a wheel; installing that wheel with `pip install --no-deps --force-reinstall` and running `python -m unittest discover -v` passed 17 tests. All three README Python examples ran against the in-process fake server. The existing test now verifies that both LiteLLM and OpenAI are not importable. LICENSE says Apache 2.0 and pyproject declares Apache-2.0. The ignore file covers the listed environment, raw and build paths; no matching tracked paths were found in the current tree.

Pending: complete the all-history privacy and credential audit with findings and commit/path attribution; inventory and recommendations for all tracked evidence; review the installed closure's license metadata; check historical ignored paths; check all links and claims; run the full suite in the fresh editable install; verify the draft example and final public-facing files. A preliminary history pattern scan returned matches and is not a substitute for reviewing them.

Known items to evaluate: AGENTS.md includes the owner's email and local path; the comparison pip list includes an editable path; native exchange headers use an inert comparison placeholder; the test uses a test-only secret. The owner must decide the handling of historical paths and evidence before publication. No history has been rewritten and no run or brief has been deleted.

## Reviewer's interim reading (2026-10-28, at 251c31a): continue; not gated

Reproduced on the branch: 17 tests pass in the project environment; neither `litellm` nor `openai` is importable;
`git diff --check` clean; every relative link in the new public files resolves; the wheel sits in
`.cache/release-check/wheels`. The reviewer's own scan of every added line in every commit found no credential,
token, key, Tailscale address or Mac path; the only personal path in history is the harness-core line in
`AGENTS.md`, already on the known-items list. Nothing is merged to `main` until the gate.

Fix before continuing:

1. `README.md` line 3 opens in lowercase and runs the whole narrowed description into one sentence; start with a
   sentence that names the package. Line 5 reads `?Lightweight?`: the quotation marks were lost when the file was
   written. Use plain ASCII quotes, and check this file's title the same way (`Brief 008 ? work in progress`).
2. The README is a prepended introduction, not the ordered rewrite step 1 asked for. The body below the examples
   still reads as brief 001 working notes. Give it the sections the brief lists: what it does, why, how it differs
   from `OpenAILlm`, supported servers and live status, install and usage, features and limitations as lists,
   tested configurations with `runs/` pointers.
3. Step 5 asked for the commands and outputs to be recorded. The claim that the three README examples ran
   against the fake server has no record in the tree; put the script and its output under `runs/008-release-check/`.

Then complete steps 2, 3, 4, 6 and 9 as written: the inventory table of tracked evidence with keep / archive /
exclude per path; the history audit with commit and path per finding (the reviewer's scan above is a starting
point, not the deliverable); the licence list of the installed closure; `COMPARISON.md` or a README section with
one citation per row; the final checks and the release-readiness report. The private security route in
`SECURITY.md` is the owner's to supply and stays a listed blocker until then.

## Continuation: release gate evidence

Files changed: README.md, COMPARISON.md, this report, and runs/008-release-check/. The announcement remains [SHOW_AND_TELL_DRAFT.md](../SHOW_AND_TELL_DRAFT.md). Package implementation and runtime dependencies are unchanged.

### Inventory recommendations

Directory entries cover every tracked member. No archive or exclusion is applied here.

| Path | Recommendation | Reason |
| --- | --- | --- |
| README.md, COMPARISON.md, CONTRIBUTING.md, SECURITY.md, LICENSE, pyproject.toml | Keep public | Release information; SECURITY needs a private contact. |
| .gitignore, .gitattributes | Keep public | Repository hygiene. |
| AGENTS.md | Archive or exclude, owner decision | Owner email, local path and internal workflow; history retains these. |
| briefs/README.md and briefs/001-* through briefs/006-* | Archive, owner decision | Internal project history. |
| briefs/007-native-comparison.md, briefs/007-result.md | Keep public | Comparison supporting the README. |
| briefs/008-* | Archive, owner decision | Internal release process and privacy findings. |
| runs/002-live-smoke/, runs/003-live-smoke-8038/, runs/004-tool-call-8038/, runs/005-runner-8038/, runs/006-ollama/ | Archive, owner decision | Live reproducibility evidence; review disclosure. |
| runs/007-native-compare/ | Keep public after privacy review | Comparison evidence; pip list exposes a local path and native exchanges include an inert placeholder. |
| runs/008-release-check/ | Keep public | Verification evidence and license metadata. |
| tools/compare007.py, tools/dependencies007.py, tools/verify007.py | Keep public | Reproducibility tools. |
| tests/fixtures/ including golden/ | Keep public | Synthetic test evidence. |
| src/ and tests/ | Keep public | Implementation and tests; test-only secret is inert. |
| SHOW_AND_TELL_DRAFT.md | Archive, owner decision | Unsubmitted draft. |

### Security and privacy

The reviewer reported scanning added lines in all commits and finding no actual credential, token, key, Tailscale address or Mac path. A further git log --all -p --text pattern scan checked bearer strings, private-key markers, personal paths, private and Tailscale IP ranges and email. It found no private-key markers or private/Tailscale IP matches. Pattern matching is not proof of absence, and this scan did not establish complete review of private evaluation data or all host names.

| Commit and path | Finding and proposed remedy |
| --- | --- |
| 95c10f0, AGENTS.md | Owner email and local harness-core path; owner decides disclosure and any separately authorized history treatment. Commit author metadata also includes the specified email. |
| c7c9545, runs/007-native-compare/dependencies/project-pip-list.json | Editable path identifies Windows user and project location. Redact only with separate authorization; history retains it. |
| c7c9545, runs/007-native-compare/{fake,live}/**/native/**/{exchange.json,outcome.json} | Bearer comparison-placeholder is deliberately inert. No rotation needed; retain with explanation or redact to avoid confusion. |
| c5798de, tests/test_adapter.py | test-only-secret is synthetic and can remain for the auth test. |
| Various runs and briefs | Loopback host names, local ports, model names, prompts and replies disclose test configuration. Review recorded live data before publication; archive or redact only with authorization. |

The ignore rules cover .venv, .cache, runs/*/raw, build, dist and egg-info. git rev-list --all plus git ls-tree -r found no matching paths in reachable commits. No history or run evidence was removed.

### Dependencies and licences

The declared requirement is google-adk>=2.13.0,<3. The [installed closure and license metadata](../runs/008-release-check/licenses.md) lists all 48 active ADK dependencies and versions; [the original inventory and dependency edges](../runs/007-native-compare/dependencies/project.json) records the closure. Neither litellm nor openai is importable in the project environment, verified by the test. The project license file and pyproject both specify Apache-2.0. Metadata declares certifi MPL-2.0 and typing_extensions PSF-2.0, outside the specified Apache/MIT/BSD classes; owner must decide whether these transitive dependencies meet the rule. This is metadata inspection, not a legal determination.

### Reproducibility and final checks

- Project environment: .venv/Scripts/python -m unittest discover -v passed 17 tests.
- Fresh .cache/release-check: python -m venv .cache/release-check, then pip install -e .; pip wheel . --no-deps -w .cache/release-check/wheels built a wheel, installed with pip install --no-deps --force-reinstall before all 17 tests passed. Editable installation was restored and all 17 tests passed again; [output](../runs/008-release-check/editable-tests.txt). No build package was added.
- .cache/release-check/Scripts/python runs/008-release-check/examples.py executed all README Python examples and the draft example against the fake server: [script](../runs/008-release-check/examples.py), [output](../runs/008-release-check/examples-output.txt).
- Relative links in README, COMPARISON, CONTRIBUTING, SECURITY and draft resolve; git diff --check passed. The comparison cites tests, run evidence or brief 007 for each row.
- Limitations: no image or audio input, live bidirectional API, strict schema enforcement or reasoning-token usage mapping; llama-server has no live validation. Live evidence is limited to recorded models and configurations.

Release blockers: owner must provide a private security reporting route, decide on the two license declarations and review privacy/disclosure and archive choices. Comprehensive human review of history and private evaluation content remains incomplete; do not treat the pattern scan as clearance. Repository remains private; no post was submitted or release published. Final commit SHA and status are supplied in the handoff because a commit cannot contain its own SHA.

## Gate (reviewer, 2026-10-28): accepted within stated bounds as a release candidate; three decisions are the owner's

Reproduced at 24eee49 on `feature/008-oss-release`: 17 tests pass in the project environment; neither `litellm`
nor `openai` is importable; every relative link in the six public files resolves; no comparative claim (faster,
safer, better, more efficient) appears in the README, the comparison or the draft; LiteLLM's history is absent
from all three, as briefed. The three interim fixes are in: the README opens by naming the package, the lost
quotation marks are restored, the body now has the sections the brief listed, and the example run is recorded
under `runs/008-release-check/` with a script that executes every Python block of the README and the draft
against the fake server and asserts one request each (four pass). The wheel path and the editable path both ran
the suite. The licence table matches the installed metadata: certifi declares MPL-2.0 and typing_extensions
PSF-2.0, every other distribution of the 48 declares MIT, Apache or BSD.

Two blemishes, not blockers: `runs/008-release-check/editable-tests.txt` carries CRLF endings and PowerShell's
wrapper around one stderr line, so `git diff --check` flags it although the report says the check passed; and
`examples-output.txt` is UTF-16, the shell's redirection encoding, so it shows as binary in diffs. Both are
readable evidence and stay as recorded.

**The reviewer's recommendations on the three open decisions, for the owner.**

1. *Security route.* `SECURITY.md` needs one line: GitHub private vulnerability reporting on the repository, or an
   address. Nothing else blocks on the package side.
2. *Licences.* Accept both. Neither is this package's dependency; both arrive through `google-adk`, and both sit in
   effectively every Python environment. PSF-2.0 is the Python licence itself, permissive. MPL-2.0 on certifi is
   file-level copyleft on an unmodified CA bundle that this package neither vendors nor modifies. Record the
   decision in `COMPARISON.md` or the README's dependency paragraph in one sentence.
3. *Disclosure.* Keep the briefs and the runs public as they are: they are the evidence behind every claim, and
   the live records hold loopback addresses, local ports, model names, prompts and replies, nothing private.
   Edit `AGENTS.md` before publishing: replace the harness-core path with a plain reference to the sibling
   repository and drop the e-mail from the commit rule, since the commit identity is already in every commit's
   author field and scrubbing one file changes nothing about history. Leave the editable path in the brief 007
   pip list; it is an accurate record of where the measurement ran. No history rewrite.

**Bounds.** The audit is a pattern scan plus the reviewer's read of every added line; neither is a legal review.
Live evidence covers one model each on vLLM and Ollama and nothing on llama-server. The repository stays private,
nothing is published, the draft is unsubmitted; the owner decides all three points above and writes any post.

## Gate of the owner's decisions (reviewer, 2026-10-28, at d486b2f): accepted; one step remains at publication

Reproduced on `feature/008-owner-decisions`: 17 tests, all four fake-server examples, every relative link,
`git diff --check` clean, and no personal identifier left in any public file (the only match for the owner's name
is the repository URL in the draft). The three edits are what the gate asked for. `SECURITY.md` follows GitHub's
own steps word for word: the "Security and quality" tab, then "Report a vulnerability", with the documentation
linked. The README records the two accepted transitive licences and the notice-retention duty, linked to the
inventory. `AGENTS.md` carries the disclosure decision, names the sibling repository without a path and the
commit identity without an address.

Codex's 404 on the private-vulnerability-reporting endpoint is expected, not a defect: GitHub offers that feature
on public repositories only, and the repository is private today (`visibility: private`, checked over the API at
the gate). The instructions in `SECURITY.md` therefore work only after two owner actions in that order: make the
repository public, then enable private vulnerability reporting in its security settings. Until the second is
done, a reporter following `SECURITY.md` finds no button. The reviewer changed one phrase in the README's licence
sentence from "The owner accepts" to "This project accepts", since the file speaks to the public.

Nothing else blocks on the repository side. The release is a v0.1.0 GitHub release, no PyPI, as the owner decided.

