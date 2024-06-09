import os
import os.path
import asyncio
from aiogram import Router, F, types
from aiogram.types import Message, FSInputFile
from aiogram.filters.command import Command

import db.orm
from config.config_reader import config
from filters.is_user import IsUserFilter
from openai_operations import ai_actions as api
from data.runtime_info import UsersRuntimeInfo
from db import orm

router = Router()
info = UsersRuntimeInfo()


@router.message(F.voice)
async def voice_msg(message: Message):

    # запись в БД
    await db.orm.update_user_voice_message_count(message.from_user.id)

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
        if message.chat.id not in info.data:
            thread = await api.create_thread()
            info.data[message.chat.id] = thread
        else:
            thread = info.data[message.chat.id]
        new_message = await api.add_message(text=text_from_audio, thread=thread)
        based_run = await api.create_run(info.based_assistant, thread)
        values_run = await api.create_run(info.values_assistant, thread)

        # вернётся текстовый ответ на вопрос пользователя
        based_response = await api.get_final_result(thread=thread, run=based_run)

        # поиск ценностей, их валидация и сохранение
        await api.get_final_result(thread=thread,
                                   run=values_run,
                                   user_message_text=text_from_audio,
                                   user_id=message.from_user.id)

        # конвертация текста в голосовое
        response_audio = await api.from_text_to_audio(based_response, new_message.id)
        wrapper = FSInputFile(path=response_audio)

        # отправка пользователю
        await bot.send_voice(voice=wrapper, chat_id=message.chat.id)

        # финальные операции
        os.remove(response_audio)

    except Exception as e:
        await message.answer('Произошла некоторая неполадка. Пожалуйста, повторите ваш запрос')
        if message.chat.id == config.admin:
            await message.answer(f'{e}')
        else:
            await message.bot.send_message(chat_id=config.admin,
                                           text=f'ОШИБКА у пользователя:\n'
                                                f'id: {message.chat.id}\n'
                                                f'ник: {message.chat.username}\n'
                                                f'\n'
                                                f'{e}')
    finally:
        await message.bot.delete_message(chat_id=message.chat.id,
                                         message_id=reminder_to_wait.message_id)


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
