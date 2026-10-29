# Brief 010 — the llama-server knob, then the caveat comes off

**Why.** Brief 009 validated the `llama_server` profile live on llama.cpp 0.8.0 with LFM3-1.7B: text and tools,
plain and streamed, and both `Runner` round trips passed with ids preserved. It also found that the profile's one
documented knob, `extra_body={"reasoning_format": "none"}`, which the README's llama-server example recommends,
made the server answer HTTP 400 `Failed to initialize samplers` on both server settings. Every one of those
requests also carried the fixed fixture's `response_format: json_object`, so the finding is the combination, not
the knob alone. The package cannot drop its "model-free only" caveat while its own example sends a field that
errored in the only live test. This brief settles the knob in at most six requests, fixes the package accordingly,
and then updates the public surfaces to what brief 009 proved. The owner's word for the live calls and for the
server start is this brief.

**Steps.**

1. **Same server, same tunnel, same preconditions as brief 009** (its step 1 and 2 verbatim, with `--reasoning off`).
2. **Isolate the knob.** Four requests at most, all the fixed text request **without** `response_format`:
   (a) no `extra_body`; (b) `extra_body={"reasoning_format": "none"}`; then restart the server once without
   `--reasoning off` and repeat (c) and (d). Record every exchange under `runs/010-llama-server-knob/` as before.
   Read llama-server's README at the `b11960` tag for what `reasoning_format` means as a request field, and quote
   it in the result.
3. **Fix the package to the finding.**
   - If `reasoning_format: none` succeeds without JSON mode: keep the knob, and in `profiles.py` and the README
     state that it must not be combined with `response_mime_type="application/json"` on llama.cpp 0.8.0, citing the
     recorded 400. Add a model-free test that the adapter refuses that combination for the `llama_server` profile
     with an `INVALID_REQUEST`-class error before any request is sent, so the server never sees it.
   - If it fails without JSON mode too: remove `reasoning_format` from the `llama_server` knob set and from the
     README example, document that reasoning is a server-side setting (`--reasoning off` or `--reasoning-format`
     on the command line, cited to llama-server's README), and adjust the golden fixtures and tests accordingly.
   Either way the request bodies in `tests/fixtures/golden/llama_server-*.json` must match what the adapter now
   sends, and the 17 tests plus any new one pass.
4. **Public surfaces.** Replace "llama-server was tested model-free only" in the README, `COMPARISON.md` and
   `SHOW_AND_TELL_DRAFT.md` with the fact: validated live on one model, LFM3-1.7B Q4_K_M, on llama.cpp 0.8.0
   (tag b11960) with `--jinja --reasoning off`, pointing at `runs/009-llama-server/`. Set `version = "0.1.1"` in
   `pyproject.toml`. State the knob rule from step 3 in the README's llama-server paragraph.
5. **Report.** `briefs/010-result.md`: the four readings, the quoted README text, the fix chosen and why, the test
   count, and the final `pgrep -af llama-server` reading. Both servers stopped by PID; the Jetson as found.

**Bounds.** At most six completion requests and two identity reads. The only server started is brief 009's, on
127.0.0.1:8111, at most twice. Package changes limited to the `llama_server` profile's knob handling, its tests
and fixtures, the four public surfaces and the version. No change to the `vllm` or `ollama` profiles. Branch
`feature/010-llama-server-knob` from `main`; the owner's commit identity and the usual tail; no push; deliver the
branch and the SHA, then stop. The owner tags 0.1.1.
