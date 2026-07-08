"""Streaming responses — token by token, like ChatGPT."""
import os
from apilane import Apilane

client = Apilane(api_key=os.environ["APILANE_API_KEY"])

stream = client.chat.completions.create(
    model="claude-3-5-sonnet",
    messages=[{"role": "user", "content": "Write a haiku about programming."}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
print()
