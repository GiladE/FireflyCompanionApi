from datetime import datetime
from ulid import ULID
from enum import Enum
from pynamodb.attributes import UnicodeAttribute, JSONAttribute
from pynamodb_attributes import UnicodeEnumAttribute
from .base import Base


class EventType(Enum):
    CHAT_MESSAGE = 0
    STATE_UPDATE__CARGO = 1
    UNKNOWN = 9999


class CargoType(Enum):
    NONE = 0
    FUEL = 1
    PART = 2
    CARGO = 3
    CONTRA = 4
    UNKNOWN = 9999


# PK = GAME::<game_id:str>
# SK = EVENT::<event_id:str>

# GSI1PK = CONNECTION::<connection_id:str>
# GSI1SK = CONNECTION::<connection_id:str>


class Event(Base, discriminator="event"):
    game_id = UnicodeAttribute()
    event_id = UnicodeAttribute()
    data = JSONAttribute()
    event_type = UnicodeEnumAttribute(
        EventType,
        EventType.UNKNOWN,
    )

    @classmethod
    def find(self, game_id, event_id):
        try:
            return self.query(
                f"GAME::{game_id}",
                self.SK == f"EVENT::{event_id}",
                limit=1,
            ).next()
        except StopIteration as exc:
            raise Event.DoesNotExist() from exc

    @classmethod
    def new(self, **args):
        event_id = f"{datetime.utcnow().isoformat()}#{ULID()}"
        return self(
            f"GAME::{args['game_id']}",
            f"EVENT::{event_id}",
            **args,
        )
