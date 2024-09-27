from src.db.connection import Connection
from src.services.apigateway import (
    broadcast_message_to_connections,
    create_broadcast_message,
    params,
    respond,
)

connection = Connection()


def connect(event, _context):
    connection_id = event["requestContext"]["connectionId"]
    channel_id = params(event, "channel_id")

    if not channel_id:
        return respond(400, "Missing 'channel_id' in query string parameters")

    if connection.create_connection(channel_id, connection_id):
        return respond(200)
    else:
        return respond(500, "Failed to store connection")


def disconnect(event, _context):
    connection_id = event["requestContext"]["connectionId"]

    if connection.delete(connection_id):
        return respond(200)
    else:
        return respond(500, "Failed to remove connection")


def message(event, _context):
    connection_id = event["requestContext"]["connectionId"]
    message = event.get("body")
    connection = connection.find(connection_id)

    if not connection:
        return respond(404, "Connection not found")

    connections = connection.find_by_channel_id(connection["channel_id"])

    if connections is None:
        return respond(500, "Failed to retrieve connections")

    broadcast_message = create_broadcast_message(connection_id, message)

    if broadcast_message_to_connections(connections, broadcast_message):
        return respond(200)
    else:
        return respond(500, "Failed to broadcast message")
