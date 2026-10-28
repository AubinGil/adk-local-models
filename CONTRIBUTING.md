# Contributing

Use Python 3.11 or later in an isolated environment:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m unittest discover -v
```

Changes need a model-free test using the fixture server. Cite vendor documentation for server-specific knobs, and discuss any new dependency before adding it. Live servers are independently managed; do not change their configuration as part of a test.
