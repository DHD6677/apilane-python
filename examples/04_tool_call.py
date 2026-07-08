"""Tool calling — let the model call your Python function."""
import json
import os
from apilane import Apilane

client = Apilane(api_key=os.environ["APILANE_API_KEY"])


def get_weather(city: str, unit: str = "celsius") -> dict:
    # In real life, call a weather API here.
    return {"city": city, "unit": unit, "temp": 22, "condition": "sunny"}


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["city"],
            },
        },
    }
]

resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
    tool_choice="auto",
)

msg = resp.choices[0].message
if msg.tool_calls:
    call = msg.tool_calls[0]
    args = json.loads(call.function.arguments)
    result = get_weather(**args)
    print(f"Model called {call.function.name}({args}) -> {result}")
else:
    print(msg.content)
