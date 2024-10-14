from pynamodb.attributes import UnicodeAttribute, JSONAttribute
from .base import Base


# PK = GAME::<game_id:str>
# SK = State::<state_id:str>


class State(Base, discriminator="state"):
    game_id = UnicodeAttribute()
    state_id = UnicodeAttribute()
    data = JSONAttribute()

    @classmethod
    def find(cls, game_id, state_id):
        try:
            return cls.query(
                f"GAME::{game_id}",
                cls.SK == f"STATE::{state_id}",
                limit=1,
            ).next()
        except StopIteration as exc:
            raise State.DoesNotExist() from exc

    @classmethod
    def upsert(cls, game_id, state_id, state_data):
        try:
            obj = cls.find(game_id, state_id)
        except State.DoesNotExist():
            obj = cls(f"GAME::{game_id}", f"STATE::{state_id}")

        obj.data = state_data
        obj.save()
