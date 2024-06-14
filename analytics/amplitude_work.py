import logging
from amplitude import Amplitude, Identify, BaseEvent
from concurrent.futures import ThreadPoolExecutor
from config.config_reader import config

client = Amplitude(config.amplitude_api_key)
client.configuration.logger = logging.getLogger(__name__)

# отдельный поток для отслеживания ивентов
amplitude_executor = ThreadPoolExecutor(max_workers=1)

event_types = {
    1: 'Start Clicked',
    2: 'Del Clicked',
    3: 'Voice message',
    4: 'Image message',
    5: 'Other message',
    6: 'New user added to db',
    7: 'Edit voice'
}


def track_event(event_type_number, user_id):
    try:
        event_type = event_types[event_type_number]
        event = BaseEvent(event_type=event_type, user_id=str(user_id))
        client.track(event)
    except Exception as e:
        logging.error(e)

