from src.services.router import message_action


@message_action("auth", "login")
def login(body, event, context):
    return {"statusCode": 200, "body": "Login successful"}


@message_action("auth", "logout")
def logout(body, event, context):
    return {"statusCode": 200, "body": "Logout successful"}
