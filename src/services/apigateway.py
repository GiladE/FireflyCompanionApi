import json
import boto3
from datetime import datetime
from src.db.connection import Connection

connection = Connection()

apigw_client = boto3.client(
    "apigatewaymanagementapi",
    endpoint_url="https://ws.cortexrelay.quest",
)


def create_broadcast_message(connection_id, message):
    """Create a broadcast message in the required format."""
    return json.dumps(
        {
            "time": datetime.utcnow().isoformat(),
            "user": connection_id,
            "message": message,
        }
    )


def broadcast_message_to_connections(connections, message):
    """Broadcast the message to all connections in the channel."""
    success = True
    for connection in connections:
        try:
            apigw_client.post_to_connection(
                ConnectionId=connection["connection_id"], Data=message.encode("utf-8")
            )
            print(
                f"Message sent to connection: connection_id={connection['connection_id']}"
            )
        except apigw_client.exceptions.GoneException:
            print(
                f"Stale connection detected, deleting: connection_id={connection['connection_id']}"
            )
            connection.delete(connection["channel_id"], connection["connection_id"])
        except Exception as e:
            print(
                f"Failed to send message to connection {connection['connection_id']}: {str(e)}"
            )
            success = False
    return success


def params(event, key):
    """Get 'key' from query string parameters."""
    query_string_params = event.get("queryStringParameters", {})
    return query_string_params.get(key)


def respond(status_code, message=None):
    """Generate an HTTP response."""
    response = {"statusCode": status_code}
    if message:
        response["body"] = message
    return response
