import logging
from amplitude import Amplitude, Identify, BaseEvent
from concurrent.futures import ThreadPoolExecutor
from config.config_reader import config

client = Amplitude(config.amplitude_api_key)
client.configuration.logger = logging.getLogger(__name__)

# отдельный поток для отслеживания ивентов
amplitude_executor = ThreadPoolExecutor(max_workers=1)


def command_start_event(user_id):
    event = BaseEvent(event_type="Start Clicked", user_id=str(user_id))
    client.track(event)


def del_context_event(user_id):
    event = BaseEvent(event_type="Del Clicked", user_id=str(user_id))
    client.track(event)


def voice_message_event(user_id):
    event = BaseEvent(event_type="Voice message", user_id=str(user_id))
    client.track(event)


def image_message_event(user_id):
    event = BaseEvent(event_type="Image message", user_id=str(user_id))
    client.track(event)


def other_message_event(user_id):
    event = BaseEvent(event_type="Other message", user_id=str(user_id))
    client.track(event)


def add_to_db_event(user_id):
    event = BaseEvent(event_type="New user added to db", user_id=str(user_id))
    client.track(event)




