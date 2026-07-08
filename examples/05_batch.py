"""Batch — fire many requests concurrently with async."""
import asyncio
import os
from apilane import AsyncApilane


async def main():
    async with AsyncApilane(api_key=os.environ["APILANE_API_KEY"]) as client:
        prompts = [
            "Translate 'hello' to French.",
            "Translate 'hello' to Japanese.",
            "Translate 'hello' to Spanish.",
            "Translate 'hello' to German.",
            "Translate 'hello' to Russian.",
        ]
        tasks = [
            client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": p}],
                max_tokens=30,
            )
            for p in prompts
        ]
        results = await asyncio.gather(*tasks)
        for prompt, r in zip(prompts, results):
            print(f"{prompt:<40} -> {r.choices[0].message.content}")


if __name__ == "__main__":
    asyncio.run(main())
