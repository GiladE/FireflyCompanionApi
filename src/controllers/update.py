from src.services.router import message_action


@message_action("gs", "DisgruntleCrew")
def disgruntle(body, event, context):
    return {"statusCode": 200, "body": "Update processed"}
