"""Hash exact HTTP entity bytes (not headers or HTTP chunk framing)."""

import hashlib
import json


def encode_body(value: dict) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def metadata(request: bytes, reply: bytes, identity: dict | None, profile: str,
             *, complete: bool = True) -> dict:
    return {"request_sha256": sha256(request), "reply_sha256": sha256(reply),
            "server_identity": identity, "profile": profile,
            "reply_complete": complete}
