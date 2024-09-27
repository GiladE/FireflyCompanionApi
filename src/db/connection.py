import os
from datetime import datetime, timedelta
from . import BaseModel


class Connection(BaseModel):
    table_name = os.environ.get("CONNECTIONS_TABLE")
    partition_key = "channel_id"
    sort_key = "connection_id"

    def create_connection(self, channel_id, connection_id):
        """Store the connection in the DynamoDB table with a TTL."""
        ttl = int((datetime.utcnow() + timedelta(days=3)).timestamp())
        item = {
            self.partition_key: channel_id,
            self.sort_key: connection_id,
            "ttl": ttl,
            "connected_at": datetime.utcnow().isoformat(),
        }
        return self.create(item)

    def find_by_channel_id(self, channel_id):
        """Retrieve all connections for the given channel_id."""
        return self.find(pk_value=channel_id)
