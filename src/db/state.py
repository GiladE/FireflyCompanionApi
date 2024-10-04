import os
from . import BaseModel


class DBState(BaseModel):
    table_name = os.environ.get("STATE_TABLE")
    partition_key = "game_id"
    sort_key = "state_id"

    def upsert(self, game_id, state_id, state_data):
        """Upsert 'state' by state_id based on the provided state."""
        found_state = self.find(state_id)

        if found_state:
            found_state["data"] = state_data
            if self.update(
                game_id,
                {"data": state_data},
                state_id,
            ):
                return found_state
        else:
            item = {
                self.partition_key: game_id,
                "data": state_data,
            }
            if self.create(item):
                return item

        return None
