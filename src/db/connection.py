from datetime import timedelta
from pynamodb.attributes import UnicodeAttribute, TTLAttribute
from .base import Base

# PK = CHANNEL::<channel_id:str>
# SK = CONNECTION::<connection_id:str>

# GSI1PK = CONNECTION::<connection_id:str>
# GSI1SK = CONNECTION::<connection_id:str>


class Connection(Base, discriminator="connection"):
    channel_id = UnicodeAttribute()
    connection_id = UnicodeAttribute()

    ttl = TTLAttribute(default=timedelta(hours=10))

    @classmethod
    def get_by_channel(self, channel_id, **args):
        return self.query(
            f"CHANNEL::{channel_id}",
            self.SK.startswith(f"CONNECTION::"),
            **args,
        )

    @classmethod
    def find(self, connection_id):
        try:
            return self.gsi1.query(
                f"CONNECTION::{connection_id}",
                self.GSI1SK == f"CONNECTION::{connection_id}",
                limit=1,
            ).next()
        except StopIteration as exc:
            raise Connection.DoesNotExist() from exc

    @classmethod
    def new(self, **args):
        return self(
            f"CHANNEL::{args['channel_id']}",
            f"CONNECTION::{args['connection_id']}",
            GSI1PK=f"CONNECTION::{args['connection_id']}",
            GSI1SK=f"CONNECTION::{args['connection_id']}",
            **args,
        )
