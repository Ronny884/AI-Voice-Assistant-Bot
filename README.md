## AI Voice Assistant Bot

Telegram чат-бот на Aiogram, который способен принимать голосовые сообщения, преобразовывать их в текст, 
получать ответы на заданные вопросы и озвучивать ответы обратно пользователю с использованием асинхронного клиента OpenAI API.
Помимо этого бот способен идентифицировать ценности пользователя и асинхронно сохранять их в БД PostgreSQL.

Использованы следующие сервисы OpenAI API:
1. Whisper (OpenAI API) для конвертации голосового сообщения в текст.
2. OpenAI Assistant API для получения ответов на вопросы и нахождения ценностей. 
3. OpenAI TTS API для озвучки полученных ответов.
4. OpenAI Chat Completions для валидации найденных ценностей.

Ссылка на бота: https://t.me/VeryGoodAIBot
