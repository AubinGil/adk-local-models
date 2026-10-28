# Brief 008 ? work in progress

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

