import os
from . import BaseModel


class Event(BaseModel):
    table_name = os.environ.get("EVENTS_TABLE")
    partition_key = "game_id"
    sort_key = "id"

    def create_event(self, game_id, event_id, payload):
        """Store the event in the DynamoDB table."""
        item = {
            self.partition_key: game_id,
            self.sort_key: event_id,
            "payload": payload,
        }
        return self.create(item)

    def find_event(self, game_id, event_id):
        """Retrieve the event for the given game_id and event_id."""
        return self.find(pk_value=game_id, sk_value=event_id)
