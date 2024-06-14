import os
import os.path
import asyncio
from pathlib import Path
from openai_operations.ai_actions import client
from openai_operations.prompts import *


class FileWorker:
    @staticmethod
    async def create_vector_store():
        vector_store = await client.beta.vector_stores.create(
            name="Documentation"
        )
        print('vs:', vector_store.id)
        return vector_store

    @staticmethod
    async def add_file_to_vector_store(vector_store_id):
        path_to_file = os.path.join(Path(__file__).parent, 'alarm_doc.docx')
        with open(path_to_file, 'rb') as file:
            file_batch = await client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store_id, files=[file]
            )
            print(file_batch.status)
            print(file_batch.file_counts)

    @staticmethod
    async def update_assistant(assistant_id, vector_store_id):
        assistant = await client.beta.assistants.update(
            assistant_id=assistant_id,
            tools=[{"type": "file_search"}, {"type": "code_interpreter"}, save_value_json],
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
        )
        return assistant


