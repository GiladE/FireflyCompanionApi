import json
from src.db.connection import DBConnection
from src.db.event import DBEvent, EventType
from src.db.game import DBGame
from src.services.apigateway import (
    broadcast_message_to_connections,
    create_broadcast_data,
    params,
    respond,
)

Connection = DBConnection()
Game = DBGame()
Event = DBEvent()


def connect(event, _context):
    connection_id = event["requestContext"]["connectionId"]
    game_code = params(event, "channel_id")

    if not game_code:
        return respond(400, "Missing 'game_code' in query string parameters")

    game = Game.find_or_create(game_code)

    if game and Connection.create_connection(game["game_id"], connection_id):
        return respond(200)
    else:
        return respond(500, "Failed to store connection")


def disconnect(event, _context):
    connection_id = event["requestContext"]["connectionId"]

    if Connection.delete(connection_id):
        return respond(200)
    else:
        return respond(500, "Failed to remove connection")


def message(event, _context):
    active_connection_id = event["requestContext"]["connectionId"]
    message_body = event.get("body")

    try:
        message_data = json.loads(message_body)
    except json.JSONDecodeError:
        return respond(400, "Json body missing.")

    active_connection = Connection.find_by_connection_id(active_connection_id)

    if not active_connection:
        return respond(404, "Connection not found")

    try:
        event_type = EventType(message_data["type"])
    except:
        event_type = EventType.UNKNOWN

    event_created = Event.create_event(
        game_id=active_connection["channel_id"],
        event_type=event_type.value,
        data={
            "sender": active_connection_id,
            **message_data,
        },
    )

    if not event_created:
        return respond(500, "Failed to store event")

    recipient_connections = Connection.find_by_channel_id(
        active_connection["channel_id"]
    )

    if recipient_connections is None:
        return respond(500, "Failed to retrieve connections")

    broadcast_message = create_broadcast_data(active_connection_id, message_data)

    if broadcast_message_to_connections(recipient_connections, broadcast_message):
        return respond(200)
    else:
        return respond(500, "Failed to broadcast message")
