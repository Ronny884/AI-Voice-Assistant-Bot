import asyncio
from openai_operations.prompts import *


class UserMoodFinder:
    def __init__(self, client, photo_base64):
        self.client = client
        self.photo = photo_base64

    async def get_mood(self):
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": mood_finding_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{self.photo}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300
        )
        return response.choices[0].message.content

