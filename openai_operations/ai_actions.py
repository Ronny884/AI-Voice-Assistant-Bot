import json
import asyncio
from pathlib import Path
from openai import AsyncOpenAI
from openai_operations.prompts import *
from openai_operations.validation import Validator
from config.config_reader import config
from db import orm

client = AsyncOpenAI(api_key=config.openai_api_key)


class AudioWork:
    @staticmethod
    async def from_audio_to_text(audio_file):
        transcription = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
        return transcription

    @staticmethod
    async def from_text_to_audio(text, msg_id):
        speech_file_path = Path(__file__).parent / f"speech_{msg_id}.mp3"
        response = await client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        response.stream_to_file(speech_file_path)
        return speech_file_path


async def create_assistant():
    assistant = await client.beta.assistants.create(
        name="assistant",
        instructions=assistant_instructions,
        model="gpt-4o",
        tools=[{"type": "code_interpreter"}, save_value_json]
    )
    return assistant


async def load_assistant():
    assistant = await client.beta.assistants.retrieve(assistant_id=config.assistant_id)
    return assistant


async def create_thread():
    thread = await client.beta.threads.create()
    return thread


async def add_message(text, thread):
    message = await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=text
    )
    return message


async def create_run(assistant, thread):
    run = await client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    return run


async def get_final_result(thread, run, user_message_text=None, user_id=None):
    if run.status == 'completed':
        answer = await get_answer_from_messages(thread, run)
        return answer

    elif run.status == 'requires_action':
        tool = run.required_action.submit_tool_outputs.tool_calls[0]
        if tool.function.name == "save_value":
            values = json.loads(tool.function.arguments)['values']

            # вызов функции для валидации и сохранения
            await save_value(user_id, values, user_message_text)

            final_run = await client.beta.threads.runs.submit_tool_outputs_and_poll(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=[{"tool_call_id": tool.id, "output": ""}])

            if final_run.status == 'completed':
                answer = await get_answer_from_messages(thread, final_run)
                return answer

    else:
        return Exception


async def get_answer_from_messages(thread, run):
    messages = await client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id)
    try:
        answer = messages.to_dict()['data'][0]['content'][0]['text']['value']
    except:
        answer = messages.to_dict()['data'][0]['content']
    return answer


async def save_value(user_id, values, user_message):
    validator = Validator(client=client,
                          user_message=user_message,
                          values=values)

    # определяем, можно ли сохранять ценности в БД
    boolean = await validator.get_boolean_result()
    if boolean:
        values_list = [word.strip() for word in values.split(',')]
        for value in values_list:
            value_exists = await orm.value_exists(user_id, value)
            if value_exists:
                await orm.update_value_rating(user_id, value)
            else:
                await orm.insert_value(user_id, value)







