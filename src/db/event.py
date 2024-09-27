import os
from datetime import datetime
from enum import Enum
from . import BaseModel


class EventType(Enum):
    CHAT_MESSAGE = "CHAT_MESSAGE"


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
            "payload": data,
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
        }
        return self.create(item)

    def generate_unique_id(self):
        """Generate a unique identifier for the event."""
        # Implement a method to generate a unique ID, e.g., UUID4
        import uuid

        return str(uuid.uuid4())

    def find_event(self, game_id, event_id):
        """Retrieve the event for the given game_id and event_id."""
        return self.find(pk_value=game_id, sk_value=event_id)
