"""Documented profile knobs; no server settings are changed by this package."""

from copy import deepcopy
from typing import Literal

Profile = Literal["vllm", "ollama", "llama_server"]
PREFIXES = {"vllm/": "vllm", "ollama/": "ollama", "llama-server/": "llama_server"}
DEFAULT_URLS = {
    "vllm": "http://localhost:8000/v1",
    "ollama": "http://localhost:11434/v1",
    "llama_server": "http://localhost:8080/v1",
}

# vLLM: extra_body={"chat_template_kwargs": {"enable_thinking": False}}.
# Template-specific: https://docs.vllm.ai/en/v0.22.0/features/reasoning_outputs/
# Ollama: extra_body={"reasoning_effort": "none"} disables supported thinking.
# https://docs.ollama.com/api/openai-compatibility#v1chatcompletions
# keep_alive and native think are NOT documented chat-completions fields:
# https://docs.ollama.com/api/chat (native endpoint; outside this adapter).
# llama-server: extra_body={"reasoning_format": "none"} returns raw text.
# Tools require an owner-configured --jinja and a compatible tool-use template.
# https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
# No thinking defaults: support and valid values depend on the served model.
PROFILE_KNOBS = {
    "vllm": {"chat_template_kwargs"},
    "ollama": {"reasoning_effort", "reasoning"},
    "llama_server": {"reasoning_format", "chat_template_kwargs", "reasoning_effort"},
}


def apply_extra(body: dict, profile: Profile, extra_body: dict) -> dict:
    """Copy extensions without allowing them to replace mapped request fields."""
    if profile not in DEFAULT_URLS:
        raise ValueError(f"Unknown profile: {profile}")
    if extra_body.keys() & (body.keys() | {"stream_options"}):
        raise ValueError("extra_body must not override mapped request fields")
    if profile == "ollama" and extra_body.keys() & {"keep_alive", "think"}:
        raise ValueError("Ollama chat completions documents reasoning_effort, not keep_alive/think")
    foreign = set.union(*PROFILE_KNOBS.values()) - PROFILE_KNOBS[profile]
    if extra_body.keys() & foreign:
        raise ValueError(f"Profile knob is not documented for {profile}")
    return deepcopy(body) | deepcopy(extra_body)
