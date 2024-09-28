import os
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
from . import BaseModel


class DBConnection(BaseModel):
    table_name = os.environ.get("CONNECTIONS_TABLE")
    partition_key = "channel_id"
    sort_key = "connection_id"

    def create_connection(self, channel_id, connection_id):
        """Store the connection in the DynamoDB table with a TTL."""
        ttl = int((datetime.utcnow() + timedelta(hours=10)).timestamp())
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

    def find_by_connection_id(self, connection_id):
        """Retrieve the connection using the GSI on connection_id."""
        try:
            response = self.table.query(
                IndexName="ConnectionIdIndex",
                KeyConditionExpression=Key("connection_id").eq(connection_id),
            )
            items = response.get("Items", [])
            if not items:
                print(f"Connection not found: connection_id={connection_id}")
                return None
            return items[0]
        except Exception as e:
            print(f"Failed to retrieve connection: {str(e)}")
            return None
