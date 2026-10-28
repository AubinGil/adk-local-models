"""Pure ADK / chat-completions conversions.

Wire contract: https://docs.ollama.com/api/openai-compatibility
and https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
"""

import json
from copy import deepcopy

from google.adk.models.llm_response import LlmResponse
from google.genai import types


def json_schema(schema) -> dict:
    """Convert Gemini Schema, retaining property names and JSON-schema aliases."""
    if hasattr(schema, "model_dump"):
        schema = schema.model_dump(mode="json", by_alias=True, exclude_none=True)
    aliases = {"any_of": "anyOf", "additional_properties": "additionalProperties",
               "defs": "$defs", "ref": "$ref"}

    def convert(node):
        if isinstance(node, list):
            return [convert(x) for x in node]
        if not isinstance(node, dict):
            return node
        result = {}
        for key, value in node.items():
            if key in ("nullable", "propertyOrdering", "property_ordering"):
                continue
            key = aliases.get(key, key)
            if key == "type":
                result[key] = value.lower() if isinstance(value, str) else value
            elif key in ("properties", "$defs"):
                result[key] = {name: convert(child) for name, child in value.items()}
            elif key in ("default", "enum", "example", "examples"):
                result[key] = deepcopy(value)
            else:
                result[key] = convert(value)
        if node.get("nullable"):
            result = {"anyOf": [result, {"type": "null"}]}
        return result

    return convert(schema)


def _text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(_text(x) for x in value)
    parts = value.parts if isinstance(value, types.Content) else [value]
    if any(p.text is None for p in parts or []):
        raise ValueError("Only text system instructions are supported")
    return "".join(p.text for p in parts or [])


def request_body(request, model: str, stream: bool = False) -> dict:
    messages = []
    config = request.config
    if config.system_instruction is not None:
        messages.append({"role": "system", "content": _text(config.system_instruction)})
    pending = []
    sequence = 0
    for content in request.contents:
        if content.role not in ("user", "model"):
            raise ValueError(f"Unsupported content role: {content.role}")
        text, calls, responses = [], [], []
        for part in content.parts or []:
            if part.text is not None:
                text.append(part.text)
            elif part.function_call is not None:
                if content.role != "model":
                    raise ValueError("Function calls require model role")
                call = part.function_call
                sequence += 1
                call_id = call.id or f"call_{sequence}"
                if any(p[0] == call_id for p in pending):
                    raise ValueError("Duplicate pending tool call id")
                pending.append((call_id, call.name))
                calls.append({"id": call_id, "type": "function", "function": {
                    "name": call.name, "arguments": json.dumps(call.args or {},
                        ensure_ascii=False, sort_keys=True, separators=(",", ":"))}})
            elif part.function_response is not None:
                if content.role != "user":
                    raise ValueError("Function responses require user role")
                response = part.function_response
                candidates = [p for p in pending if
                              (p[0] == response.id if response.id else p[1] == response.name)]
                if len(candidates) != 1 or candidates[0][1] != response.name:
                    raise ValueError("Function response must match one pending tool call")
                match = candidates[0]
                pending.remove(match)
                responses.append({"role": "tool", "tool_call_id": match[0],
                                  "content": json.dumps(response.response, ensure_ascii=False,
                                                        sort_keys=True, separators=(",", ":"))})
            else:
                raise ValueError("Only text and function parts are supported")
        if calls and responses:
            raise ValueError("Function calls and responses require separate turns")
        messages.extend(responses)
        if text or calls:
            message = {"role": "assistant" if content.role == "model" else "user",
                       "content": "".join(text) if text else None}
            if calls:
                message["tool_calls"] = calls
            messages.append(message)
    body = {"model": model, "messages": messages, "stream": stream}
    for source, target in (("temperature", "temperature"), ("top_p", "top_p"),
                           ("max_output_tokens", "max_tokens"), ("stop_sequences", "stop")):
        value = getattr(config, source)
        if value is not None:
            body[target] = value
    if config.response_mime_type == "application/json":
        body["response_format"] = {"type": "json_object"}
    tools = []
    for tool in config.tools or []:
        if not isinstance(tool, types.Tool) or not tool.function_declarations:
            raise ValueError("Only function declaration tools are supported")
        for declaration in tool.function_declarations:
            function = {"name": declaration.name}
            if declaration.description is not None:
                function["description"] = declaration.description
            if declaration.parameters_json_schema is not None:
                function["parameters"] = deepcopy(declaration.parameters_json_schema)
            elif declaration.parameters is not None:
                function["parameters"] = json_schema(declaration.parameters)
            else:
                function["parameters"] = {"type": "object", "properties": {}}
            tools.append({"type": "function", "function": function})
    if tools:
        body["tools"] = tools
    if stream:
        body["stream_options"] = {"include_usage": True}
    return body


def response_from_body(body: dict) -> LlmResponse:
    choice = body["choices"][0]
    message = choice["message"]
    parts = []
    if message.get("content") is not None:
        if not isinstance(message["content"], str):
            raise ValueError("Expected text content")
        if message["content"]:
            parts.append(types.Part(text=message["content"]))
    for call in message.get("tool_calls") or []:
        if call.get("type") != "function":
            raise ValueError("Unsupported tool call type")
        if not call.get("id") or not call["function"].get("name"):
            raise ValueError("Tool calls require an id and function name")
        args = json.loads(call["function"]["arguments"])
        if not isinstance(args, dict):
            raise ValueError("Function arguments must be a JSON object")
        parts.append(types.Part(function_call=types.FunctionCall(
            id=call["id"], name=call["function"]["name"], args=args)))
    reason = {"stop": types.FinishReason.STOP, "tool_calls": types.FinishReason.STOP,
              "length": types.FinishReason.MAX_TOKENS,
              "content_filter": types.FinishReason.SAFETY}.get(
                  choice.get("finish_reason"), types.FinishReason.OTHER)
    usage = body.get("usage")
    return LlmResponse(content=types.Content(role="model", parts=parts), partial=False,
                       finish_reason=reason, usage_metadata=(
        types.GenerateContentResponseUsageMetadata(
            prompt_token_count=usage.get("prompt_tokens"),
            candidates_token_count=usage.get("completion_tokens"),
            total_token_count=usage.get("total_tokens")) if usage else None))


class StreamAccumulator:
    """Accumulate indexed tool deltas without exposing incomplete calls to ADK."""

    def __init__(self):
        self.text = ""
        self.calls = {}
        self.finish_reason = None
        self.usage = None

    def add(self, body: dict) -> str:
        if body.get("usage") is not None:
            self.usage = body["usage"]
        if not body["choices"]:
            return ""
        choice = body["choices"][0]
        delta = choice.get("delta", {})
        text = delta.get("content") or ""
        self.text += text
        for fragment in delta.get("tool_calls") or []:
            call = self.calls.setdefault(fragment["index"], {
                "id": "", "type": "function", "function": {"name": "", "arguments": ""}})
            for key in ("id", "type"):
                if fragment.get(key):
                    call[key] = fragment[key]
            for key in ("name", "arguments"):
                call["function"][key] += fragment.get("function", {}).get(key) or ""
        if choice.get("finish_reason"):
            self.finish_reason = choice["finish_reason"]
        return text

    def finish(self) -> LlmResponse:
        if self.finish_reason is None:
            raise ValueError("Stream ended without a finish reason")
        return response_from_body({"choices": [{"message": {
            "content": self.text, "tool_calls": [self.calls[k] for k in sorted(self.calls)]},
            "finish_reason": self.finish_reason}], "usage": self.usage})
