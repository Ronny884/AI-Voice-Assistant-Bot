import asyncio
from pathlib import Path
from openai import AsyncOpenAI
from openai_operations.prompts import *
from openai_operations.validation import Validator
from config.config_reader import config
from db import orm

client = AsyncOpenAI(api_key=config.openai_api_key)


async def from_audio_to_text(audio_file):
    transcription = await client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )
    return transcription


async def create_based_assistant():
    based_assistant = await client.beta.assistants.create(
        name="based_assistant",
        instructions=based_assistant_instructions,
        model="gpt-4o",
        tools=[{"type": "code_interpreter"}]
    )
    return based_assistant


async def create_values_assistant():
    values_assistant = await client.beta.assistants.create(
        name="values_assistant",
        instructions=values_assistant_instructions,
        model="gpt-4o",
        tools=[{"type": "code_interpreter"}, save_value_assistant_api_function_json]
    )
    return values_assistant


async def load_based_assistant():
    based_assistant = await client.beta.assistants.retrieve(assistant_id=config.based_assistant_id)
    return based_assistant


async def load_values_assistant():
    values_assistant = await client.beta.assistants.retrieve(assistant_id=config.values_assistant_id)
    return values_assistant


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


async def submit_empty_output(thread_id, run_id, tool_id):
    run = await client.beta.threads.runs.submit_tool_outputs_and_poll(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=[{"tool_call_id": tool_id, "output": ' '}]
    )
    return run


async def get_final_result(thread, run, user_message_text=None, user_id=None):
    if run.status == 'completed':
        messages = await client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id)
        try:
            answer = messages.to_dict()['data'][0]['content'][0]['text']['value']
        except:
            answer = messages.to_dict()['data'][0]['content']
        return answer
    else:
        # в данном случае статус будет required_action, говорящий
        # о том, что была вызвана функция ассистента save_value
        try:
            tool = run.required_action.submit_tool_outputs.tool_calls[0]
            if tool.function.name == "save_value":

                # поскольку функция save_value вызывается лишь для сохранения ценностей из
                # содержательных сообщений, то нам не требуется интегрировать какие-либо
                # данные в результат, ввиду чего output может быть пустым
                run = await submit_empty_output(thread.id, run.id, tool.id)
                if run.status == 'completed':
                    messages = await client.beta.threads.messages.list(thread_id=thread.id)
                    values = messages.to_dict()['data'][0]['content'][0]['text']['value']
                    await save_value(user_id, values, user_message_text)
        except:
            return 'No values'


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


async def from_text_to_audio(text, msg_id):
    speech_file_path = Path(__file__).parent / f"speech_{msg_id}.mp3"
    response = await client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    response.stream_to_file(speech_file_path)
    return speech_file_path




