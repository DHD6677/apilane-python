"""Basic chat completion — the hello world of apilane."""
import os
from apilane import Apilane

client = Apilane(api_key=os.environ["APILANE_API_KEY"])

resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ],
    temperature=0.2,
    max_tokens=100,
)
print(resp.choices[0].message.content)
print("Tokens used:", resp.usage.total_tokens)
