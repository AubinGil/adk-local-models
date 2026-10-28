"""Three fixed requests for the committed wire goldens."""

from google.adk.models.llm_request import LlmRequest
from google.genai import types

KNOBS = {"vllm": {"chat_template_kwargs": {"enable_thinking": False}},
         "ollama": {"reasoning_effort": "none"},
         "llama_server": {"reasoning_format": "none"}}


def fixed_requests():
    declaration = types.FunctionDeclaration(name="weather", description="Get weather",
        parameters=types.Schema(type="OBJECT", properties={
            "city": types.Schema(type="STRING", description="City name")}, required=["city"]))
    config = types.GenerateContentConfig(system_instruction="Be concise.", temperature=0,
        top_p=0.9, max_output_tokens=32, stop_sequences=["END"], response_mime_type="application/json")
    user = types.Content(role="user", parts=[types.Part(text="Weather in Paris?")])
    text = LlmRequest(contents=[user], config=config)
    tools_config = config.model_copy(deep=True)
    tools_config.tools = [types.Tool(function_declarations=[declaration])]
    tools = LlmRequest(contents=[user], config=tools_config)
    history = LlmRequest(contents=[user,
        types.Content(role="model", parts=[types.Part(function_call=types.FunctionCall(
            id="call_weather", name="weather", args={"city": "Paris"}))]),
        types.Content(role="user", parts=[types.Part(function_response=types.FunctionResponse(
            id="call_weather", name="weather", response={"temperature": 20}))])],
        config=tools_config)
    return {"text": text, "tools": tools, "history": history}
