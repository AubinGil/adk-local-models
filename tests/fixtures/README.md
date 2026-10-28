These synthetic protocol fixtures are authored for model-free tests. They are
not captured from a model or the owner's servers. JSON and SSE pairs have the
same text/tool output, finish reason and usage. Hashes cover the fixture bytes,
including their line endings. The fake server records exact received POST bytes
and exact replayed response bytes. Goldens are fixed expected POST entities,
compared as bytes, with no regeneration during tests.
