# Brief 009 — the `llama_server` profile live, on the Jetson's llama.cpp 0.8.0

**Why.** Every public surface of 0.1.0 says the llama-server profile was tested model-free only: the README, the
comparison page, the release notes and the announcement draft. The caveat is honest and it is the one hole left.
The owner's Jetson Orin Nano Super (JetPack 7.2) now carries llama.cpp 0.8.0, tag b11960, built for CUDA under
`~/llama.cpp-lfm3`, with `LFM3-1.7B-Q4_K_M.gguf` verified under `~/models/lfm3/`. Probes on 2026-10-28 showed the
model answers, calls tools and completes a tool round trip on that server, and that it reasons by default unless
the server runs with `--reasoning off`. This brief runs the same smoke the vLLM and Ollama profiles received in
briefs 003 to 006 through the `llama_server` profile, and checks the profile's documented knob against a real
server. The owner's word for the live calls and for starting the one server named below is this brief.

**Steps.**

1. **Preconditions, read-only, over `ssh gildas01@100.126.229.13`.** No `llama-server` process running
   (`pgrep -af llama-server` empty), `ollama ps` showing no resident model, at least 2.5 GB in the `available`
   column of `free -m`. If any fails, record the reading in `runs/009-llama-server/README.md` and stop; stop
   nothing on the Jetson.
2. **Start the server.** Exactly this, detached, output to `~/lfm3-tests/009-server.log`:

   ```
   PATH=/usr/local/cuda/bin:$PATH ~/llama.cpp-lfm3/build/bin/llama-server \
     -m ~/models/lfm3/LFM3-1.7B-Q4_K_M.gguf -a lfm3-1.7b --host 127.0.0.1 --port 8111 \
     -c 4096 -np 1 -ngl 99 --no-warmup --jinja --reasoning off
   ```

   Wait for `/health`. Record the PID, `llama-server --version` and the command in the run README. Reach it from
   the workstation through `ssh -N -L 8111:127.0.0.1:8111 gildas01@100.126.229.13`; the adapter's `base_url` is
   `http://127.0.0.1:8111/v1`, profile `llama_server`, model `lfm3-1.7b`. Nothing is exposed beyond loopback.
3. **The smoke, as in briefs 003 and 004.** One identity read, then the fixed text request plain and streamed and
   the fixed tools request (the weather declaration) plain and streamed, with the same generation config as
   those briefs and no `extra_body`. Then **the Runner round trips, as in brief 005**: `LlmAgent` with the
   deterministic `weather` tool, `Runner.run_async`, one plain and one streamed, fresh `InMemorySessionService`
   each, the same instruction and message as 005. Record every exchange as before: `request.bin`, `reply.bin`,
   `exchange.json`, `custom_metadata.json`, session and yielded events for the Runner turns, a `summary.json`
   and a `verification.json` that recomputes every hash.
4. **The knob.** The profile documents `extra_body={"reasoning_format": "none"}` as "returns raw text" and
   cites llama-server's README. Send the fixed text request once more with that `extra_body` against the running
   server and diff the reply against step 3's. Then, once, stop this server, start it again with the same command
   minus `--reasoning off`, and send the fixed text request twice: without `extra_body` and with
   `reasoning_format: none`. Record whether `reasoning_content` appears, whether the answer text is empty at the
   32-token fixture limit, and what the request-level knob changed. Stop that server too. This answers whether the
   documented knob does what the profile says on 0.8.0, which the README must then state plainly either way.
5. **Readings and report.** `runs/009-llama-server/README.md` with the two server commands, the request count and
   the readings table; `briefs/009-result.md` with the result per request, the knob finding, and the bounds. If
   every request in step 3 succeeds with a parsed tool call and both round trips complete, update the four public
   surfaces so that llama-server is stated as validated live on one model, naming the model and build, and remove
   the "model-free only" caveat from README, `COMPARISON.md` and `SHOW_AND_TELL_DRAFT.md`; set `version = "0.1.1"`
   in `pyproject.toml`. If anything fails, change no public surface and report the failure with its bytes. The
   release notes of 0.1.0 stay as they are; the owner tags 0.1.1.
6. **Leave the Jetson as found.** Both servers this brief started are stopped by their PIDs; `pgrep -af
   llama-server` is empty at the end and the reading is in the run README. Nothing else on the Jetson is started,
   stopped, pulled, installed or edited.

**Bounds.** At most 16 completion requests and three identity reads across the two server runs. The only server
started is the one named above, on 127.0.0.1:8111, twice; nothing on the speech pipeline, Ollama or the old
`~/llama.cpp` build is touched. Package code unchanged; the only package edits are the four public surfaces and
the version, and only on full success. Branch `feature/009-llama-server-live` from `main`; the owner's commit
identity and the usual tail; no push; deliver the branch and the SHA, then stop.
