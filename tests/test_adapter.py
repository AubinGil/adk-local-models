import asyncio
import importlib.util
import json
import socket
import unittest
from hashlib import sha256

from google.adk.agents import LlmAgent
from google.adk.models.llm_request import LlmRequest
from google.adk.models.registry import LLMRegistry
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from adk_local_models import OpenAICompatibleLlm
from adk_local_models.mapping import json_schema, request_body, response_from_body, StreamAccumulator
from tests.fake_server import FakeServer, FIXTURES
from tests.requests import KNOBS, fixed_requests


def semantic(response):
    return response.model_dump(exclude={"custom_metadata"})


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Windows SSL context construction and server shutdown can exceed 100ms.
        asyncio.get_running_loop().slow_callback_duration = 5

    def model(self, server, profile="vllm", **kwargs):
        return OpenAICompatibleLlm(model="fake-model", profile=profile,
                                   base_url=server.base_url, **kwargs)

    async def collect(self, model, request=None, stream=False):
        return [r async for r in model.generate_content_async(
            request or fixed_requests()["text"], stream=stream)]

    def recording(self, response, server, index=-1):
        data = response.custom_metadata
        self.assertEqual(data["request_sha256"], sha256(server.requests[index]).hexdigest())
        self.assertEqual(data["reply_sha256"], sha256(server.responses[index]).hexdigest())
        self.assertEqual(data["server_identity"]["models"],
                         json.loads((FIXTURES / "models.json").read_bytes()))
        self.assertEqual(data["server_identity"]["reply_sha256"],
                         sha256((FIXTURES / "models.json").read_bytes()).hexdigest())
        self.assertTrue(data["reply_complete"])

    async def test_golden_requests_all_profiles(self):
        for profile, knobs in KNOBS.items():
            with FakeServer() as server:
                model = self.model(server, profile, extra_body=knobs)
                for name, request in fixed_requests().items():
                    with self.subTest(profile=profile, request=name):
                        response, = await self.collect(model, request)
                        self.assertIsNone(response.error_code)
                        self.assertEqual(server.requests[-1],
                            (FIXTURES / "golden" / f"{profile}-{name}.json").read_bytes())
                        self.recording(response, server)
                        self.assertEqual(response.custom_metadata["profile"], profile)
                self.assertEqual(server.models_reads, 1)

    async def test_plain_and_streamed_outputs(self):
        for profile in KNOBS:
            for kind in ("text", "tool"):
                with self.subTest(profile=profile, kind=kind), FakeServer(
                    f"{kind}.json", f"{kind}.sse") as server:
                    model = self.model(server, profile)
                    plain, = await self.collect(model)
                    streamed = await self.collect(model, stream=True)
                    self.assertGreater(len(streamed), 1)
                    self.assertIsNone(plain.error_code)
                    self.assertFalse(plain.partial)
                    self.assertEqual(semantic(plain), semantic(streamed[-1]))
                    self.recording(plain, server, 0)
                    self.recording(streamed[-1], server, 1)
                    for part in streamed[:-1]:
                        self.assertTrue(part.partial)
                        self.assertFalse(part.get_function_calls())
                        self.assertFalse(part.custom_metadata["reply_complete"])
                    if kind == "text":
                        self.assertEqual("".join(r.content.parts[0].text for r in streamed[:-1]),
                                         "Hello café!")
                        self.assertEqual(plain.usage_metadata.total_token_count, 11)
                    else:
                        self.assertEqual(plain.get_function_calls()[0].id, "call_weather")
                        self.assertEqual(plain.get_function_calls()[0].args, {"city": "Paris"})

    async def test_errors(self):
        for fixture, code in (("error.json", "HTTP_500"), ("malformed.json", "INVALID_RESPONSE")):
            for stream in (False, True):
                with self.subTest(fixture=fixture, stream=stream), FakeServer(fixture) as server:
                    response, = await self.collect(self.model(server), stream=stream)
                    self.assertEqual(response.error_code, code)
                    self.assertTrue(response.error_message)
                    self.assertFalse(response.partial)
                    self.recording(response, server)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
            # Bound but not listening: guarantees refusal without a port reuse race.
            model = OpenAICompatibleLlm(model="fake", base_url=f"http://127.0.0.1:{port}/v1", timeout=5)
            response, = await self.collect(model)
            self.assertEqual(response.error_code, "TRANSPORT_ERROR")
            self.assertTrue(response.error_message)
            self.assertEqual(response.custom_metadata["reply_sha256"], sha256(b"").hexdigest())
            self.assertIn("error", response.custom_metadata["server_identity"])
            self.assertEqual(response.custom_metadata["server_identity"]["error"], "ConnectError")

    async def test_identity_once_for_concurrent_calls(self):
        with FakeServer() as server:
            model = self.model(server)
            results = await asyncio.gather(self.collect(model), self.collect(model))
            self.assertTrue(all(not rs[0].error_code for rs in results))
            self.assertEqual(server.models_reads, 1)

    async def test_identity_failure_is_cached_without_blocking_generation(self):
        with FakeServer(models_fixture="error.json") as server:
            model = self.model(server)
            for _ in range(2):
                response, = await self.collect(model)
                self.assertIsNone(response.error_code)
                self.assertEqual(response.custom_metadata["server_identity"],
                                 {"error": "HTTPStatusError"})
            self.assertEqual(server.models_reads, 1)

    async def test_incomplete_stream_and_invalid_tool_reply(self):
        with FakeServer("truncated.sse", "bad-arguments.json") as server:
            model = self.model(server)
            responses = await self.collect(model, stream=True)
            self.assertTrue(responses[0].partial)
            self.assertEqual(responses[-1].error_code, "INVALID_RESPONSE")
            self.assertFalse(responses[-1].partial)
            self.recording(responses[-1], server)
            response, = await self.collect(model)
            self.assertEqual(response.error_code, "INVALID_RESPONSE")
            self.recording(response, server)

    async def test_runner_tool_turn_reaches_session(self):
        calls = []

        def weather(city: str) -> dict:
            """Get weather for a city."""
            calls.append(city)
            return {"temperature": 20}

        with FakeServer("tool.json", "text.json") as server:
            agent = LlmAgent(name="local", model=self.model(server), tools=[weather])
            sessions = InMemorySessionService()
            await sessions.create_session(app_name="adapter_tests", user_id="user", session_id="session")
            runner = Runner(agent=agent, app_name="adapter_tests", session_service=sessions)
            events = [event async for event in runner.run_async(user_id="user", session_id="session",
                new_message=types.Content(role="user", parts=[types.Part(text="Weather in Paris?")]))]
            self.assertEqual(calls, ["Paris"])
            self.assertTrue(any(e.is_final_response() and e.content.parts[0].text == "Hello café!"
                                for e in events))
            session = await sessions.get_session(app_name="adapter_tests", user_id="user", session_id="session")
            self.assertEqual(session.events[-1].content.parts[0].text, "Hello café!")
            messages = json.loads(server.requests[1])["messages"]
            tool = next(m for m in messages if m["role"] == "tool")
            self.assertEqual(tool["tool_call_id"], "call_weather")
            self.assertEqual(json.loads(tool["content"]), {"temperature": 20})
            self.assertEqual(server.models_reads, 1)

    async def test_auth_and_extensions(self):
        with FakeServer() as server:
            model = self.model(server, api_key="test-only-secret", extra_body={"seed": 42})
            response, = await self.collect(model)
            self.assertIsNone(response.error_code)
            self.assertEqual(server.headers[0]["Authorization"], "Bearer test-only-secret")
            self.assertNotIn("test-only-secret", repr(model))
            self.assertNotIn("test-only-secret", model.model_dump_json())
            self.assertEqual(json.loads(server.requests[0])["seed"], 42)

    async def test_invalid_request_does_not_contact_server(self):
        for extra in ({"model": "override"}, {"stream": True}, {"think": False}, {"keep_alive": "5m"}):
            with FakeServer() as server:
                response, = await self.collect(self.model(server, "ollama", extra_body=extra))
                self.assertEqual(response.error_code, "INVALID_REQUEST")
                self.assertFalse(server.requests)
                self.assertEqual(server.models_reads, 0)

    def test_registry_and_capabilities(self):
        LLMRegistry.register(OpenAICompatibleLlm)
        for prefix, profile in (("vllm", "vllm"), ("ollama", "ollama"), ("llama-server", "llama_server")):
            model = LLMRegistry.new_llm(f"{prefix}/organization/model")
            self.assertEqual(model.profile, profile)
            self.assertEqual(model.model, "organization/model")
            self.assertFalse(model.capabilities.output_schema_and_tools)
        self.assertIsInstance(OpenAICompatibleLlm.capabilities, property)
        with self.assertRaises(NotImplementedError):
            OpenAICompatibleLlm(model="test").connect(LlmRequest())

    def test_litellm_is_not_importable(self):
        self.assertIsNone(importlib.util.find_spec("litellm"))
        with self.assertRaises(ModuleNotFoundError):
            __import__("litellm")

    def test_schema_conversion(self):
        schema = types.Schema(type="OBJECT", properties={"type": types.Schema(type="STRING", nullable=True),
            "anyOf": types.Schema(type="ARRAY", items=types.Schema(type="INTEGER"))}, required=["type"])
        self.assertEqual(json_schema(schema), {"type": "object", "properties": {
            "type": {"anyOf": [{"type": "string"}, {"type": "null"}]},
            "anyOf": {"type": "array", "items": {"type": "integer"}}}, "required": ["type"]})

    def test_request_mapping_does_not_mutate_input(self):
        request = fixed_requests()["history"]
        before = request.model_dump()
        request_body(request, "test", True)
        self.assertEqual(request.model_dump(), before)
        request.contents[-1].parts.append(types.Part(text="Please summarize."))
        messages = request_body(request, "test")["messages"]
        self.assertEqual(messages[-2]["role"], "tool")
        self.assertEqual(messages[-1], {"role": "user", "content": "Please summarize."})

    def test_parallel_stream_tool_calls_and_split_names(self):
        accumulator = StreamAccumulator()
        accumulator.add({"choices": [{"delta": {"tool_calls": [
            {"index": 1, "id": "b", "function": {"name": "wea", "arguments": "{"}},
            {"index": 0, "id": "a", "function": {"name": "weather", "arguments": "{\"city\":"}}]}}]})
        accumulator.add({"choices": [{"delta": {"tool_calls": [
            {"index": 0, "function": {"arguments": "\"Paris\"}"}},
            {"index": 1, "function": {"name": "ther", "arguments": "\"city\":\"Rome\"}"}}]},
            "finish_reason": "tool_calls"}]})
        calls = accumulator.finish().get_function_calls()
        self.assertEqual([(c.id, c.name, c.args) for c in calls], [
            ("a", "weather", {"city": "Paris"}), ("b", "weather", {"city": "Rome"})])

    def test_idless_history_and_ambiguous_response(self):
        request = fixed_requests()["history"].model_copy(deep=True)
        request.contents[1].parts[0].function_call.id = None
        request.contents[2].parts[0].function_response.id = None
        messages = request_body(request, "test")["messages"]
        self.assertEqual(messages[-1]["tool_call_id"], messages[-2]["tool_calls"][0]["id"])
        request.contents[1].parts.append(request.contents[1].parts[0].model_copy(deep=True))
        with self.assertRaises(ValueError):
            request_body(request, "test")

    def test_finish_reasons_and_bad_tool_arguments(self):
        for reason, expected in (("stop", "STOP"), ("tool_calls", "STOP"), ("length", "MAX_TOKENS"),
                                 ("content_filter", "SAFETY"), ("new_reason", "OTHER")):
            response = response_from_body({"choices": [{"message": {"content": ""}, "finish_reason": reason}]})
            self.assertEqual(response.finish_reason.value, expected)
        body = json.loads((FIXTURES / "tool.json").read_bytes())
        body["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"] = "[]"
        with self.assertRaises(ValueError):
            response_from_body(body)
        with self.assertRaises(ValueError):
            StreamAccumulator().finish()


if __name__ == "__main__":
    unittest.main()
