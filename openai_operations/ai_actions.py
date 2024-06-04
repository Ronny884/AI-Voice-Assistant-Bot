import os
import asyncio
import aiofiles
from pathlib import Path
from openai import AsyncOpenAI
from config.config_reader import config

client = AsyncOpenAI(api_key=config.openai_api_key)


async def from_audio_to_text(audio_file):
    transcription = await client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )
    return transcription


async def create_assistant():
    assistant = await client.beta.assistants.create(
        name="Test",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4o",
    )
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


async def get_answer(thread, run):
    if run.status == 'completed':
        messages = await client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id)
        answer = messages.to_dict()['data'][0]['content'][0]['text']['value']
        return answer
    else:
        return run.status


async def from_text_to_audio(text, msg_id):
    speech_file_path = Path(__file__).parent / f"speech_{msg_id}.mp3"
    response = await client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    response.stream_to_file(speech_file_path)
    return speech_file_path




