import json
from src.db.connection import DBConnection
from src.db.event import DBEvent, EventType
from src.db.game import DBGame
from src.db.player import DBPlayer
from src.services.apigateway import (
    broadcast_message_to_connections,
    create_broadcast_data,
    params,
    respond,
)

Connection = DBConnection()
Game = DBGame()
Event = DBEvent()
Player = DBPlayer()


def connect(event, _context):
    connection_id = event["requestContext"]["connectionId"]
    game_code = params(event, "game_id")
    player_id = params(event, "player_id")

    if not game_code:
        return respond(400, "Missing 'game_id' in query string parameters")

    if not player_id:
        return respond(400, "Missing 'player_id' in query string parameters")

    game = Game.find_or_create(game_code)
    player = Player.find_or_create(game_code, player_id)

    if not player or not game:
        return respond(
            500, f"Failed to resolve game or player {game_code=} {player_id=}"
        )

    connection = Connection.create_connection(
        game["game_id"],
        connection_id,
        player_id=player_id,
        game_id=game_code,
    )

    if not connection:
        return respond(500, f"Failed to create connection")

    player_ids = Player.find_all_player_ids(game_code)

    recipient_connections = Connection.get_by_channel_id(game_code)

    if recipient_connections is None:
        return respond(500, "Failed to retrieve connections")

    broadcast_message = create_broadcast_data(
        game_code,
        {
            "operation": "Update",
            "targetStates": ["PlayerIds"],
            "ownerPlayerId": player_id,
            "playerIds": player_ids,
            "messages": None,
            "solidContacts": None,
            "goals": None,
            "warrants": None,
            "money": None,
            "cargo": None,
            "playerSupply": None,
            "inactiveJobs": None,
            "activeJobs": None,
            "completeJobs": None,
            "deckUpdates": None,
        },
    )

    broadcast_message_to_connections(recipient_connections, broadcast_message)

    return respond(200)


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
        event_type=event_type,
        data={
            "sender": active_connection_id,
            **message_data,
        },
    )

    if not event_created:
        return respond(500, "Failed to store event")

    recipient_connections = Connection.get_by_channel_id(
        active_connection["channel_id"]
    )

    if recipient_connections is None:
        return respond(500, "Failed to retrieve connections")

    broadcast_message = create_broadcast_data(active_connection_id, message_data)

    if broadcast_message_to_connections(recipient_connections, broadcast_message):
        return respond(200)
    else:
        return respond(500, "Failed to broadcast message")
