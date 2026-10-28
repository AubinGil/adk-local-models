# Brief 008 ? work in progress

The release gate is **not complete**. Do not publish on the strength of this report.

Changed: README, project description, dependency isolation test, CONTRIBUTING, SECURITY and SHOW_AND_TELL_DRAFT. The draft is in [SHOW_AND_TELL_DRAFT.md](../SHOW_AND_TELL_DRAFT.md). The private security reporting route still needs the owner's input.

The project environment ran 17 tests successfully. A fresh `.cache/release-check` environment installed with `python -m pip install -e .`; `python -m pip wheel . --no-deps -w .cache/release-check/wheels` built a wheel; installing that wheel with `pip install --no-deps --force-reinstall` and running `python -m unittest discover -v` passed 17 tests. All three README Python examples ran against the in-process fake server. The existing test now verifies that both LiteLLM and OpenAI are not importable. LICENSE says Apache 2.0 and pyproject declares Apache-2.0. The ignore file covers the listed environment, raw and build paths; no matching tracked paths were found in the current tree.

Pending: complete the all-history privacy and credential audit with findings and commit/path attribution; inventory and recommendations for all tracked evidence; review the installed closure's license metadata; check historical ignored paths; check all links and claims; run the full suite in the fresh editable install; verify the draft example and final public-facing files. A preliminary history pattern scan returned matches and is not a substitute for reviewing them.

Known items to evaluate: AGENTS.md includes the owner's email and local path; the comparison pip list includes an editable path; native exchange headers use an inert comparison placeholder; the test uses a test-only secret. The owner must decide the handling of historical paths and evidence before publication. No history has been rewritten and no run or brief has been deleted.
