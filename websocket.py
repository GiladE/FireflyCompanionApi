import json
import os
import boto3
from datetime import datetime, timedelta

# DynamoDB table name from environment variable
CONNECTIONS_TABLE = os.environ.get('CONNECTIONS_TABLE')

# Initialize DynamoDB and API Gateway Management API clients
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(CONNECTIONS_TABLE)
apigw_client = boto3.client(
    "apigatewaymanagementapi",
    endpoint_url="https://ws.cortexrelay.quest",  # Replace with your WebSocket endpoint
)

def connectHandler(event, context):
    connection_id = event["requestContext"]["connectionId"]
    channel_id = get_channel_id(event)

    if not channel_id:
        return respond(400, "Missing 'channel_id' in query string parameters")

    if store_connection(channel_id, connection_id):
        return respond(200)
    else:
        return respond(500, "Failed to store connection")

def disconnectHandler(event, context):
    connection_id = event["requestContext"]["connectionId"]
    
    if remove_connection(connection_id):
        return respond(200)
    else:
        return respond(500, "Failed to remove connection")

def defaultHandler(event, context):
    connection_id = event["requestContext"]["connectionId"]
    message = event.get("body")
    channel_id = get_channel_id_by_connection(connection_id)

    if not channel_id:
        return respond(404, "Connection not found")

    connections = get_connections_by_channel(channel_id)

    if connections is None:
        return respond(500, "Failed to retrieve connections")

    broadcast_message = create_broadcast_message(connection_id, message)

    if broadcast_message_to_channel(connections, broadcast_message):
        return respond(200)
    else:
        return respond(500, "Failed to broadcast message")

# Helper Functions

def get_channel_id(event):
    """Get the channel_id from query string parameters."""
    query_string_params = event.get("queryStringParameters", {})
    return query_string_params.get("channel_id")

def respond(status_code, message=None):
    """Generate an HTTP response."""
    response = {"statusCode": status_code}
    if message:
        response["body"] = message
    return response

def store_connection(channel_id, connection_id):
    """Store the connection in the DynamoDB table."""
    ttl = int((datetime.utcnow() + timedelta(days=3)).timestamp())
    try:
        table.put_item(
            Item={
                "channel_id": channel_id,
                "connection_id": connection_id,
                "ttl": ttl,
                "connected_at": datetime.utcnow().isoformat()
            }
        )
        print(f"Connection stored: connection_id={connection_id}, channel_id={channel_id}")
        return True
    except Exception as e:
        print(f"Failed to store connection: {str(e)}")
        return False

def remove_connection(connection_id):
    """Remove the connection from the DynamoDB table."""
    try:
        response = table.scan(
            FilterExpression="connection_id = :conn_id",
            ExpressionAttributeValues={":conn_id": connection_id}
        )
        items = response.get('Items', [])
        for item in items:
            table.delete_item(
                Key={
                    "channel_id": item["channel_id"],
                    "connection_id": connection_id
                }
            )
            print(f"Connection deleted: connection_id={connection_id}, channel_id={item['channel_id']}")
        return True
    except Exception as e:
        print(f"Failed to remove connection: {str(e)}")
        return False

def parse_body(body):
    """Parse the JSON body and handle errors."""
    if not body:
        print("Empty body received")
        return None
    
    try:
        body_data = json.loads(body)
        if not isinstance(body_data, dict):
            raise ValueError("Parsed JSON is not an object")
        return body_data
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Invalid JSON format: body={body}, error={str(e)}")
        return None

def get_channel_id_by_connection(connection_id):
    """Retrieve the channel_id for the given connection_id."""
    try:
        response = table.scan(
            FilterExpression="connection_id = :conn_id",
            ExpressionAttributeValues={":conn_id": connection_id}
        )
        items = response.get('Items', [])
        if not items:
            print(f"Connection not found: connection_id={connection_id}")
            return None
        return items[0]["channel_id"]
    except Exception as e:
        print(f"Failed to retrieve connection: {str(e)}")
        return None

def get_connections_by_channel(channel_id):
    """Retrieve all connections for the given channel_id."""
    try:
        response = table.query(
            KeyConditionExpression="channel_id = :channel_id",
            ExpressionAttributeValues={":channel_id": channel_id}
        )
        connections = response.get("Items", [])
        print(f"Connections retrieved for channel: channel_id={channel_id}, count={len(connections)}")
        return connections
    except Exception as e:
        print(f"Failed to retrieve connections: {str(e)}")
        return None

def create_broadcast_message(connection_id, message):
    """Create a broadcast message in the required format."""
    return json.dumps({
        "time": datetime.utcnow().isoformat(),
        "user": connection_id,
        "message": message
    })

def broadcast_message_to_channel(connections, message):
    """Broadcast the message to all connections in the channel."""
    success = True
    for connection in connections:
        try:
            apigw_client.post_to_connection(
                ConnectionId=connection["connection_id"],
                Data=message.encode("utf-8")
            )
            print(f"Message sent to connection: connection_id={connection['connection_id']}")
        except apigw_client.exceptions.GoneException:
            # Remove stale connections
            print(f"Stale connection detected, deleting: connection_id={connection['connection_id']}")
            table.delete_item(
                Key={
                    "channel_id": connection["channel_id"],
                    "connection_id": connection["connection_id"]
                }
            )
        except Exception as e:
            print(f"Failed to send message to connection {connection['connection_id']}: {str(e)}")
            success = False
    return success
