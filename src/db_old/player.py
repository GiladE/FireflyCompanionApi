import os
from boto3.dynamodb.conditions import Key
from . import BaseModel


class DBPlayer(BaseModel):
    table_name = os.environ.get("PLAYERS_TABLE")
    partition_key = "game_id"
    sort_key = "player_id"

    def find_or_create(self, game_id, player_id):
        """Find or create 'player' by game_id and player_id."""
        player = self.find(game_id, player_id)

        if player:
            return player

        item = {
            self.partition_key: game_id,
            self.sort_key: player_id,
        }

        if self.create(item):
            return item

        return None

    def find_all_player_ids(self, game_id):
        """
        Find all player_ids associated with a specific game_id.
        :param game_id: The ID of the game for which to retrieve all player IDs.
        :return: List of player IDs.
        """
        try:
            response = self.table.query(
                KeyConditionExpression=Key(self.partition_key).eq(game_id),
                ProjectionExpression=self.sort_key,
            )
            items = response.get("Items", [])
            player_ids = [item[self.sort_key] for item in items]
            return player_ids
        except Exception as e:
            print(f"Failed to retrieve player IDs for game_id {game_id}: {str(e)}")
            return []
