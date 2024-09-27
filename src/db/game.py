import os
from enum import Enum
from . import BaseModel


class GameStates(Enum):
    WAITING_ROOM = "WAITING_ROOM"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"


class DBGame(BaseModel):
    table_name = os.environ.get("GAMES_TABLE")
    partition_key = "game_id"

    def find_or_create(self, game_id):
        """Find or create 'game' by game_id (game code)."""
        game = self.find(game_id)

        if game:
            return game

        item = {
            self.partition_key: game_id,
            "state": GameStates.WAITING_ROOM.value,
        }

        if self.create(item):
            return item

        return None
