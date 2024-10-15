from src.services.apigateway import (
    respond,
)
from src.services.router import dispatch_message


def connect(event, _context):
    return respond(200)


def disconnect(event, _context):
    return respond(200)


def message(event, context):
    active_connection_id = event["requestContext"]["connectionId"]
    event["connectionId"] = active_connection_id
    return dispatch_message(event, context)
