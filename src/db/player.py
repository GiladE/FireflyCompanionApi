from pynamodb.attributes import UnicodeAttribute
from .base import Base


# PK = GAME::<game_id:str>
# SK = PLAYER::<player_id:str>


class Player(Base, discriminator="player"):
    game_id = UnicodeAttribute()
    player_id = UnicodeAttribute()

    @classmethod
    def find(cls, game_id, player_id):
        try:
            return cls.query(
                f"GAME::{game_id}",
                cls.SK == f"PLAYER::{player_id}",
                limit=1,
            ).next()
        except StopIteration as exc:
            raise Player.DoesNotExist() from exc

    @classmethod
    def find_or_create(cls, game_id, player_id):
        try:
            return cls.find(game_id, player_id)
        except Player.DoesNotExist:
            pass

        return cls(
            f"GAME::{game_id}",
            f"PLAYER::{game_id}",
            game_id=game_id,
            player_id=player_id,
        ).save()

    @classmethod
    def get_by_game_id(cls, game_id):
        return list(
            cls.query(
                f"GAME::{game_id}",
                cls.SK.startswith("PLAYER::"),
            )
        )
