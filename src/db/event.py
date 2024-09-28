import os
import uuid
from datetime import datetime
from enum import Enum
from . import BaseModel


class EventType(Enum):
    CHAT_MESSAGE = 0
    STATE_CARGO = 1
    UNKNOWN = 9999


class CargoType(Enum):
    NONE = 0
    FUEL = 1
    PART = 2
    CARGO = 3
    CONTRA = 4
    UNKNOWN = 9999


class DBEvent(BaseModel):
    table_name = os.environ.get("EVENTS_TABLE")
    partition_key = "game_id"
    sort_key = "id"

    def create_event(self, game_id, event_type, data):
        """Store the event in the DynamoDB table."""
        event_id = f"{datetime.utcnow().isoformat()}_{self.generate_unique_id()}"
        item = {
            self.partition_key: game_id,
            self.sort_key: event_id,
            "data": data,
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
        }
        return self.create(item)

    def generate_unique_id(self):
        """Generate a unique identifier for the event."""
        return str(uuid.uuid4())

    def find_event(self, game_id, event_id):
        """Retrieve the event for the given game_id and event_id."""
        return self.find(pk_value=game_id, sk_value=event_id)
