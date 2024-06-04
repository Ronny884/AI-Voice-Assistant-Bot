import os
import os.path
import shutil
import asyncio
from aiogram import Router, F, types
from aiogram.types import Message, FSInputFile
from aiogram.filters.command import Command
from config.config_reader import config
from filters.is_user import IsUserFilter
from openai_operations import ai_actions as api
from data.runtime_info import UsersRuntimeInfo

router = Router()
info = UsersRuntimeInfo()


@router.message(F.voice)
async def voice_msg(message: Message):
    reminder_to_wait = await message.answer('Бот обрабатывает запрос, ожидайте...')
    try:
        # подготовка аудиофайла
        file_id = message.voice.file_id
        bot = message.voice.bot
        file = await bot.get_file(file_id)
        file_path_on_telegram_server = file.file_path
        file_name = f"audio{file_id}.m4a"
        await bot.download_file(file_path_on_telegram_server, file_name)
        project_directory = await asyncio.to_thread(os.getcwd)
        path_to_audio = os.path.join(project_directory, file_name)
        audio_file = open(path_to_audio, "rb")

        # конвертация в текст
        text_from_audio = await api.from_audio_to_text(audio_file)

        # закрытие и удаление в папке
        audio_file.close()
        os.remove(path_to_audio)

        # получение текстового ответа от ассистента (с учётом состояния контекста)
        # если пользователь новый или он сбросил контекст - предварительно создаём
        # для него нового ассистента и поток
        # в противном случае добавляем сообщение в уже существующий поток
        if message.chat.id not in info.data:
            assistant = await api.create_assistant()
            thread = await api.create_thread()
            info.data[message.chat.id] = [assistant, thread]
        else:
            assistant = info.data[message.chat.id][0]
            thread = info.data[message.chat.id][1]
        new_message = await api.add_message(text=text_from_audio, thread=thread)
        run = await api.create_run(assistant, thread)
        response = await api.get_answer(thread, run)

        # конвертация текста в голосовое
        response_audio = await api.from_text_to_audio(response, new_message.id)
        wrapper = FSInputFile(path=response_audio)

        # отправка пользователю
        await bot.send_voice(voice=wrapper, chat_id=message.chat.id)

        # финальные операции
        await bot.delete_message(chat_id=message.chat.id, message_id=reminder_to_wait.message_id)
        os.remove(response_audio)

    except:
        await message.answer('Произошла некоторая неполадка. Пожалуйста, повторите ваш запрос')
        await message.bot.send_message(chat_id=config.admin,
                                       text=f'ОШИБКА у пользователя:\n'
                                            f'id: {message.chat.id}\n'
                                            f'ник: {message.chat.username}')


@router.message(Command("del"))
async def del_context(message: types.Message):
    if message.chat.id in info.data:
        del info.data[message.chat.id]
        await message.answer("Ваш контекст успешно сброшен")
    else:
        await message.answer("Ваш контекст был пуст")


@router.message()
async def reminder_to_message_type(message: Message):
    await message.answer('Ваше сообщение не является голосовым')
