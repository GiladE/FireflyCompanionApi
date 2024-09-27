import os
import boto3
from datetime import datetime, timedelta


dynamodb = boto3.resource('dynamodb')
connections_table = dynamodb.Table(os.environ.get('CONNECTIONS_TABLE'))


def find(connection_id):
    """Retrieve the connection for the given connection_id."""
    try:
        response = connections_table.scan(
            FilterExpression="connection_id = :conn_id",
            ExpressionAttributeValues={":conn_id": connection_id}
        )
        items = response.get('Items', [])
        if not items:
            print(f"Connection not found: connection_id={connection_id}")
            return None
        return items[0]
    except Exception as e:
        print(f"Failed to retrieve connection: {str(e)}")
        return None


def find_by_channel_id(channel_id):
    """Retrieve all connections for the given channel_id."""
    try:
        response = connections_table.query(
            KeyConditionExpression="channel_id = :channel_id",
            ExpressionAttributeValues={":channel_id": channel_id}
        )
        connections = response.get("Items", [])
        print(f"Connections retrieved for channel: channel_id={channel_id}, count={len(connections)}")
        return connections
    except Exception as e:
        print(f"Failed to retrieve connections: {str(e)}")
        return None


def create(channel_id, connection_id):
    """Store the connection in the DynamoDB table."""
    ttl = int((datetime.utcnow() + timedelta(days=3)).timestamp())
    try:
        connections_table.put_item(
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


def delete(connection_id):
    """Remove the connection from the DynamoDB table."""
    try:
        response = connections_table.scan(
            FilterExpression="connection_id = :conn_id",
            ExpressionAttributeValues={":conn_id": connection_id}
        )
        items = response.get('Items', [])
        for item in items:
            connections_table.delete_item(
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
