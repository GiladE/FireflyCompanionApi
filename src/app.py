import json
from src.db.connection import Connection
from src.db.event import Event, EventType
from src.services.apigateway import (
    broadcast_message_to_connections,
    create_broadcast_message,
    params,
    respond,
)

connection = Connection()
event_model = Event()


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
    active_connection_id = event["requestContext"]["connectionId"]
    message_body = event.get("body")

    try:
        message_data = json.loads(message_body)
    except json.JSONDecodeError:
        message_data = {"message": message_body}

    active_connection = connection.find_by_connection_id(active_connection_id)

    if not active_connection:
        return respond(404, "Connection not found")

    recipient_connections = connection.find_by_channel_id(
        active_connection["channel_id"]
    )

    if recipient_connections is None:
        return respond(500, "Failed to retrieve connections")

    event_payload = {
        "sender": active_connection_id,
        **message_data,
    }

    event_created = event_model.create_event(
        game_id=active_connection["channel_id"],
        event_type=EventType.CHAT_MESSAGE.value,
        data=event_payload,
    )

    if not event_created:
        return respond(500, "Failed to store event")

    broadcast_message = create_broadcast_message(active_connection_id, message_data)

    if broadcast_message_to_connections(recipient_connections, broadcast_message):
        return respond(200)
    else:
        return respond(500, "Failed to broadcast message")
