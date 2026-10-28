# Brief 002 readings

These are actual checks of only the endpoints authorized by
`briefs/002-live-smoke.md`, performed sequentially on 2026-10-28. All four checks
failed with `ConnectError`; no completion request was sent and no server state
was changed. No retries. This run makes no compatibility or answer-quality claim.

`summary.json` records endpoints, adapter identity/error markers, timestamps,
installed versions, and empty completion sample lists. Each `probe-N/` contains:

- `request.bin`: exact attempted HTTP request entity bytes (empty for GET).
- `reply.bin`: raw HTTP response entity bytes received (empty on these failures).
- `exchange.json`: method, URL, UTC start time, wall seconds, adapter identity
  marker, byte lengths, and SHA-256 values for both entities.

No HTTP status or response headers exist for these failed connections. The
adapter caches only the exception class for failed identity reads, so the records
do not diagnose the connection failure beyond `ConnectError`. No identity JSON
was received, and no server-identity hash is available. Empty-byte hashes are
entity hashes, not evidence of a server identity. Credentials were not used.

The package was used unchanged. A temporary observer wrapped httpx send/raw-read
methods solely to retain entity bytes and timing; it added no retry, proxy,
endpoint substitution, or request-body transformation. The adapter itself
performed and cached each `/v1/models` check. No completion metadata files exist
because the brief requires unreachable profiles to be skipped.

See [the result](../../briefs/002-result.md) for per-profile tables and limits.
