"""Vision — send an image URL and ask the model to describe it."""
import os
from apilane import Apilane

client = Apilane(api_key=os.environ["APILANE_API_KEY"])

messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image? Be brief."},
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/640px-Cat03.jpg"
                },
            },
        ],
    }
]

resp = client.chat.completions.create(model="gpt-4o", messages=messages)
print(resp.choices[0].message.content)
