# Brief 007 recordings

See ../../briefs/007-result.md for interpretation. Package source is unchanged.

- `fake/`: three fixed requests and error/usage/finish probes for both adapters and all profiles. Every invocation has outcome.json; exchanges include exact entity request.bin/reply.bin and hash/HTTP metadata.
- `live/`: bounded local endpoint checks and fixture requests; native Runner outcome contains yielded/session events and tool execution records.
- `dependencies/`: pip lists, installed file sizes, dependency closure and raw requirement edges for both isolated environments.
- `fixtures/`: additional reasoning usage and finish-reason cases derived from the existing text fixture.
- `wire-diffs.json`, `response-comparison.json`, `verification.json`: machine-readable differences and byte checks.
- `manifest.json`: source hashes, authorization, request budget accounting and version context.

Reproduce model-free work from repository root with `.cache/native-compare/Scripts/python tools/compare007.py --fake`; use the separate environment with `google-adk[openai]==2.13.0` and OpenAI 2.54.0. The tool imports this checkout via sys.path rather than installing dependencies into the project environment. Capture uses a supplied AsyncOpenAI client with request hooks and a shared httpx send/raw observer; the observer preserves response streaming and records encoded HTTP entity bytes before SDK parsing. No automatic retries.

Run `.venv/Scripts/python tools/verify007.py` for independent byte verification and recursive wire diffs. Dependency reports: run `tools/dependencies007.py project` with project Python and `tools/dependencies007.py native` with isolated Python, then capture each Python's `-m pip list --format=json`. Do not rerun live requests without a fresh budget: the existing run has used almost all its allowance. `--live --profile vllm` supports the owner's sequential server switch; counts persist in manifest.json.
