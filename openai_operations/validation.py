import asyncio
from openai_operations.prompts import *


class Validator:
    def __init__(self, client, user_message, values):
        self.client = client
        self.user_message = user_message
        self.values = values
        self.prompt = \
            f"""
            Текст сообщения пользователя: '{self.user_message}',
            Ценности: '{self.values} \n'
            {main_part_of_validation_prompt}
            """

    async def create_chat_completion(self):
        chat_completion = await self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": self.prompt
                }
            ],
            model="gpt-4o",
            tools=[validate_completions_api_function_json]
        )
        return chat_completion

    async def get_boolean_result(self):
        chat_completion = await self.create_chat_completion()
        tool_calls = chat_completion.choices[0].message.tool_calls
        if tool_calls:
            return True
        else:
            return False
