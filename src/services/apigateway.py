import json
import boto3
# from src.db.connection import DBConnection

# Connection = DBConnection()

apigw_client = boto3.client(
    "apigatewaymanagementapi",
    endpoint_url="https://ws.cortexrelay.quest",
)


def create_broadcast_data(connection_id, data):
    """Create a broadcast data in the required format."""
    return json.dumps(
        {
            "sender": connection_id,
            **data,
        }
    )


def broadcast_message_to_connections(connections, message):
    """Broadcast the message to all connections in the channel."""
    success = True
    for recipient_connection in connections:
        try:
            apigw_client.post_to_connection(
                ConnectionId=recipient_connection["connection_id"],
                Data=message.encode("utf-8"),
            )
            print(
                f"Message sent to connection: connection_id={recipient_connection['connection_id']}"
            )
        # except apigw_client.exceptions.GoneException:
        #     print(
        #         f"Stale connection detected, deleting: connection_id={recipient_connection['connection_id']}"
        #     )
        #     Connection.delete(
        #         recipient_connection["channel_id"],
        #         recipient_connection["connection_id"],
        #     )
        #     success = False
        except Exception as e:
            print(
                f"Failed to send message to connection {recipient_connection}: {str(e)}"
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
    print(f"[{status_code}] {json.dumps(response)}")
    return response
