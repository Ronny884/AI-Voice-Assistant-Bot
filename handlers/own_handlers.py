import os
import os.path
import asyncio
import aiofiles
import base64
import redis
from aiogram import Router, F, types
from aiogram.types import Message, FSInputFile
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from config.config_reader import config
from openai_operations import ai_actions as api
from openai_operations.mood_finder import UserMoodFinder
from data.runtime_info import UsersRuntimeInfo
from analytics.amplitude_work import *
from db import orm

router = Router()
info = UsersRuntimeInfo()


@router.message(F.voice)
async def voice_msg(message: Message, state: FSMContext):
    # ивент на голосовое сообщение
    amplitude_executor.submit(track_event, 3, message.from_user.id)

    # операции в БД: увеличение счётчика сообщений и получение типа голоса
    await orm.update_user_message_count(message.from_user.id)
    voice_type = await orm.get_voice(message.from_user.id)

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

        with open(path_to_audio, "rb") as audio_file:
            # конвертация в текст
            text_from_audio = await api.AudioWork.from_audio_to_text(audio_file)

        # удаление в папке
        os.remove(path_to_audio)

        # получение текстового ответа от ассистента
        # (с учётом состояния контекста из RedisStorage)
        data = await state.get_data()
        thread_id = data.get('thread_id')

        if thread_id is None:
            thread = await api.create_thread()
            await state.update_data(thread_id=thread.id)
        else:
            thread = await api.load_thread(thread_id)
        new_message = await api.add_message(text=text_from_audio, thread=thread)
        run = await api.create_run(info.assistant, thread)

        # получение ответа, валидация, сохранение в БД
        response = await api.get_final_result(thread=thread,
                                              run=run,
                                              user_message_text=text_from_audio,
                                              user_id=message.from_user.id)

        # конвертация текста в голосовое
        response_audio = await api.AudioWork.from_text_to_audio(text=response,
                                                                msg_id=new_message.id,
                                                                voice=voice_type)
        wrapper = FSInputFile(path=response_audio)

        # отправка пользователю
        await bot.send_voice(voice=wrapper, chat_id=message.chat.id)

        # удаление в папке
        os.remove(response_audio)

    except Exception as e:
        await del_context(message, state, True)
        await exception_handling(message, e)
    finally:
        await message.bot.delete_message(chat_id=message.chat.id,
                                         message_id=reminder_to_wait.message_id)


@router.message(F.photo)
async def photo_msg(message: Message, state: FSMContext):
    # ивент на сообщение с картинкой
    amplitude_executor.submit(track_event, 4, message.from_user.id)

    # запись в БД
    await orm.update_user_message_count(message.from_user.id)

    reminder_to_wait = await message.answer('Бот обрабатывает фото, ожидайте...')
    try:
        # подготовка файла
        file_id = message.photo[-1].file_id
        bot = message.bot
        file = await bot.get_file(file_id)
        file_path_on_telegram_server = file.file_path
        file_name = f"image{file_id}.png"
        await bot.download_file(file_path_on_telegram_server, file_name)
        project_directory = await asyncio.to_thread(os.getcwd)
        path_to_photo = os.path.join(project_directory, file_name)

        async with aiofiles.open(path_to_photo, "rb") as photo:
            base64_image = base64.b64encode(await photo.read()).decode('utf-8')

        # определение настроения
        mood_finder = UserMoodFinder(api.client, base64_image)
        mood = await mood_finder.get_mood()
        await message.answer(mood)

        # удаление в папке
        os.remove(path_to_photo)

    except Exception as e:
        await del_context(message, state, True)
        await exception_handling(message, e)
    finally:
        await message.bot.delete_message(chat_id=message.chat.id,
                                         message_id=reminder_to_wait.message_id)


@router.message(Command("del"))
async def del_context(message: types.Message, state: FSMContext, error_or_start=False):
    # ивент на сброс контекста
    amplitude_executor.submit(track_event, 2, message.from_user.id)

    if error_or_start:
        await state.clear()
    else:
        data = await state.get_data()
        thread_id = data.get('thread_id')

        if thread_id is not None:
            await state.clear()
            await message.answer("Ваш контекст успешно сброшен")
        else:
            await message.answer("Ваш контекст был пуст")


@router.message(Command("voice"))
async def edit_bot_voice(message: types.Message):
    # ивент на изменение настроек голоса бота
    amplitude_executor.submit(track_event, 7, message.from_user.id)

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Женский",
        callback_data="alloy")
    )
    builder.add(types.InlineKeyboardButton(
        text="Мужской",
        callback_data="echo")
    )
    await message.answer(
        "Выберете голос, которым будет отвечать бот:",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == 'alloy')
async def process_callback_button_alloy(callback: types.CallbackQuery):
    await orm.set_voice(callback.from_user.id, 'alloy')
    await callback.answer("Настройки изменены")
    await callback.message.answer("Установлен женский голос бота")


@router.callback_query(F.data == 'echo')
async def process_callback_button_echo(callback: types.CallbackQuery):
    await orm.set_voice(callback.from_user.id, 'echo')
    await callback.answer("Настройки изменены")
    await callback.message.answer("Установлен мужской голос бота")


@router.message()
async def reminder_to_message_type(message: Message):
    await message.answer('Ваше сообщение не является голосовым или содержащим фото')

    # ивент на сообщение иного рода
    amplitude_executor.submit(track_event, 5, message.from_user.id)

    # запись в БД
    await orm.update_user_message_count(message.from_user.id)


async def exception_handling(message, exception):
    await message.answer('Произошла некоторая неполадка. Пожалуйста, повторите ваш запрос')
    if message.chat.id == config.admin:
        await message.answer(f'{exception}')
    else:
        await message.bot.send_message(chat_id=config.admin,
                                       text=f'ОШИБКА у пользователя:\n'
                                            f'id: {message.chat.id}\n'
                                            f'ник: {message.chat.username}\n'
                                            f'\n'
                                            f'{exception}')
