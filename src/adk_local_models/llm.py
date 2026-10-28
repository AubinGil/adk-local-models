"""Async chat-completions transport, using ADK's existing httpx dependency."""

import asyncio
import json
from collections.abc import AsyncGenerator
from typing import Literal
from urllib.parse import urlsplit

import httpx
from google.adk.models.base_llm import BaseLlm
from google.adk.models._capabilities import LlmCapabilities
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from pydantic import Field, PrivateAttr, model_validator

from .mapping import StreamAccumulator, request_body, response_from_body
from .profiles import DEFAULT_URLS, PREFIXES, apply_extra
from .recording import encode_body, metadata, sha256


class OpenAICompatibleLlm(BaseLlm):
    profile: Literal["vllm", "ollama", "llama_server"] = "vllm"
    base_url: str = ""
    api_key: str | None = Field(default=None, repr=False, exclude=True)
    extra_body: dict = Field(default_factory=dict)
    timeout: float = Field(default=60.0, gt=0)

    _identity: dict | None = PrivateAttr(default=None)
    _identity_lock: asyncio.Lock = PrivateAttr(default_factory=asyncio.Lock)

    @model_validator(mode="after")
    def _configure(self):
        for prefix, profile in PREFIXES.items():
            if self.model.startswith(prefix):
                if "profile" in self.model_fields_set and self.profile != profile:
                    raise ValueError("Model prefix conflicts with profile")
                self.profile = profile
                self.model = self.model[len(prefix):]
                break
        if not self.model:
            raise ValueError("Model name is required")
        self.base_url = (self.base_url or DEFAULT_URLS[self.profile]).rstrip("/")
        url = urlsplit(self.base_url)
        if url.scheme not in ("http", "https") or not url.netloc or url.query or url.fragment:
            raise ValueError("base_url must be an HTTP(S) API root without query or fragment")
        if url.username or url.password:
            raise ValueError("Use api_key rather than URL credentials")
        return self

    @property
    def capabilities(self) -> LlmCapabilities:
        return LlmCapabilities(output_schema_and_tools=False)

    @classmethod
    def supported_models(cls) -> list[str]:
        # Registry uses regex fullmatch, so prefixes require the trailing .+.
        return [r"vllm/.+", r"ollama/.+", r"llama-server/.+"]

    async def _read_identity(self, client):
        async with self._identity_lock:
            if self._identity is not None:
                return
            try:
                async with client.stream("GET", self.base_url + "/models") as reply:
                    raw = b"".join([chunk async for chunk in reply.aiter_raw()])
                    reply.raise_for_status()
                    self._identity = {"models": json.loads(raw), "reply_sha256": sha256(raw),
                                      "server": reply.headers.get("server")}
            except (httpx.HTTPError, ValueError) as exc:
                # Cache failures too: do not repeatedly probe an unavailable endpoint.
                self._identity = {"error": type(exc).__name__}

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        request, raw = b"", bytearray()
        complete = False
        try:
            body = apply_extra(request_body(llm_request, self.model, stream),
                               self.profile, self.extra_body)
            request = encode_body(body)
            headers = {"Content-Type": "application/json", "Accept-Encoding": "identity"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            # Ignore environment proxy variables; local server requests stay direct.
            async with httpx.AsyncClient(timeout=self.timeout, headers=headers,
                                         trust_env=False) as client:
                await self._read_identity(client)
                async with client.stream("POST", self.base_url + "/chat/completions",
                                         content=request) as reply:
                    if not reply.is_success or not stream:
                        async for chunk in reply.aiter_raw():
                            raw.extend(chunk)
                        complete = True
                        reply.raise_for_status()
                        result = response_from_body(json.loads(bytes(raw)))
                    else:
                        accumulator = StreamAccumulator()
                        buffer = b""
                        event_data = []
                        done = False
                        async for chunk in reply.aiter_raw():
                            raw.extend(chunk)
                            buffer += chunk
                            while b"\n" in buffer:
                                line, buffer = buffer.split(b"\n", 1)
                                line = line.rstrip(b"\r")
                                if line.startswith(b"data:"):
                                    event_data.append(line[5:].removeprefix(b" "))
                                elif not line and event_data:
                                    data = b"\n".join(event_data)
                                    event_data = []
                                    if data == b"[DONE]":
                                        done = True
                                        continue
                                    if done:
                                        raise ValueError("SSE data after [DONE]")
                                    event = json.loads(data)
                                    text = accumulator.add(event)
                                    has_tool_delta = any(c.get("delta", {}).get("tool_calls")
                                                         for c in event["choices"])
                                    if text or has_tool_delta:
                                        yield LlmResponse(
                                            content=types.Content(role="model", parts=(
                                                [types.Part(text=text)] if text else [])),
                                            partial=True, custom_metadata=metadata(
                                                request, bytes(raw), self._identity, self.profile,
                                                complete=False))
                        complete = True
                        if buffer.strip() or event_data or not done:
                            raise ValueError("Incomplete SSE response")
                        result = accumulator.finish()
            result.custom_metadata = metadata(request, bytes(raw), self._identity, self.profile)
            yield result
        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError, AttributeError) as exc:
            if isinstance(exc, httpx.HTTPStatusError):
                code = f"HTTP_{exc.response.status_code}"
            elif isinstance(exc, httpx.HTTPError):
                code = "TRANSPORT_ERROR"
            else:
                code = "INVALID_RESPONSE" if request else "INVALID_REQUEST"
            yield LlmResponse(error_code=code, error_message=str(exc) or type(exc).__name__, partial=False,
                              custom_metadata=metadata(request, bytes(raw), self._identity,
                                                       self.profile, complete=complete))
