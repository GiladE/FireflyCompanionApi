import boto3
from boto3.dynamodb.conditions import Key


class BaseModel:
    dynamodb = boto3.resource("dynamodb")

    table_name = None  # abstract
    partition_key = None  # abstract
    sort_key = None  # abstract

    def __init__(self):
        if not self.table_name:
            raise ValueError("Table name must be set in the subclass.")
        self.table = self.dynamodb.Table(self.table_name)

    def find(self, pk_value, sk_value=None):
        """Retrieve an item by partition key and optional sort key."""
        key_condition = Key(self.partition_key).eq(pk_value)
        if self.sort_key and sk_value:
            key_condition &= Key(self.sort_key).eq(sk_value)
        try:
            response = self.table.query(KeyConditionExpression=key_condition)
            items = response.get("Items", [])
            if not items:
                print(
                    f"Item not found: {self.partition_key}={pk_value}, {self.sort_key}={sk_value}"
                )
                return None

            if len(items) != 1:
                print(
                    f"Item not found. More than one item matched: {self.partition_key}={pk_value}, {self.sort_key}={sk_value}"
                )
                return None

            return items[0]
        except Exception as e:
            print(f"Failed to retrieve item: {str(e)}")
            return None

    def get(self, pk_value, sk_value=None):
        """Retrieve items by partition key and optional sort key."""
        key_condition = Key(self.partition_key).eq(pk_value)
        if self.sort_key and sk_value:
            key_condition &= Key(self.sort_key).eq(sk_value)
        try:
            response = self.table.query(KeyConditionExpression=key_condition)
            items = response.get("Items", [])
            if not items:
                print(
                    f"Item not found: {self.partition_key}={pk_value}, {self.sort_key}={sk_value}"
                )
                return None

            return items
        except Exception as e:
            print(f"Failed to retrieve item: {str(e)}")
            return None

    def create(self, item):
        """Store the item in the DynamoDB table."""
        try:
            self.table.put_item(Item=item)
            print(f"Item stored: {item}")
            return True
        except Exception as e:
            print(f"Failed to store item: {str(e)}")
            return False

    def delete(self, pk_value, sk_value=None):
        """Remove the item from the DynamoDB table."""
        key = {self.partition_key: pk_value}
        if self.sort_key and sk_value:
            key[self.sort_key] = sk_value
        try:
            self.table.delete_item(Key=key)
            print(f"Item deleted: {key}")
            return True
        except Exception as e:
            print(f"Failed to delete item: {str(e)}")
            return False

    def update(self, pk_value, updates, sk_value=None):
        """
        Update an item in the DynamoDB table.
        :param pk_value: Partition key value
        :param updates: Dictionary of attributes to update with format {"attribute": "new_value"}
        :param sk_value: Optional sort key value
        :return: True if update is successful, False otherwise
        """
        key = {self.partition_key: pk_value}
        if self.sort_key and sk_value:
            key[self.sort_key] = sk_value

        update_expression = "SET " + ", ".join([f"{k} = :{k}" for k in updates.keys()])
        expression_attribute_values = {f":{k}": v for k, v in updates.items()}

        try:
            self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
            )
            print(f"Item updated: {key} with {updates}")
            return True
        except Exception as e:
            print(f"Failed to update item: {str(e)}")
            return False
