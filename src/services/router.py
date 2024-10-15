import json
import importlib
from pathlib import Path
from prettytable import PrettyTable


_action_registry = {}


def print_dict_as_table(data):
    table = PrettyTable()
    table.field_names = ["Namespace", "Action"]
    table.align = "l"

    for key, values in data.items():
        for i, value in enumerate(values):
            table.add_row([key, value], divider=(i == len(values) - 1))

    print(table)


def message_action(namespace, action=None):
    """Decorator for registering message actions."""
    def decorator(func):
        if namespace not in _action_registry:
            _action_registry[namespace] = {}
        action_key = action or '*'
        _action_registry[namespace][action_key] = func
        return func
    return decorator


def load_controllers():
    """Dynamically loads all controllers in the controllers directory."""
    controllers_path = Path(__file__).parent.parent / "controllers"
    for py_file in controllers_path.glob("*.py"):
        module_name = f"src.controllers.{py_file.stem}"
        importlib.import_module(module_name)
    print("Registered socket actions")
    print_dict_as_table({k: list(v.keys())
                        for (k, v) in _action_registry.items()})


def dispatch_message(event, context):
    """Main function for dispatching messages based on the event payload."""
    try:
        # Extract the action and body from the message
        message_body = event.get("body", "{}")
        message_data = json.loads(message_body)
        action = message_data.get("action", "")
        body = message_data.get("body", [])

        namespace, action_name = action.split(
            '/') if '/' in action else (action, None)

        # Find the appropriate handler
        namespace_actions = _action_registry.get(namespace)
        if namespace_actions:
            handler = namespace_actions.get(
                action_name) or namespace_actions.get('*')
            if handler:
                response = handler(body, event, context)
                print(f"{response=}")
                return response
            else:
                response = {
                    "statusCode": 404,
                    "body": f"Action '{action_name}' not found in namespace '{namespace}'.",
                }
                print(f"{response=}")
                return response
        else:
            response = {
                "statusCode": 404,
                "body": f"Namespace/action not found.",
            }
            print(f"{response=}")
            return response
    except json.JSONDecodeError:
        response = {
            "statusCode": 400,
            "body": "Invalid JSON format.",
        }
        print(f"{response=}")
        return response
    except Exception as e:
        response = {
            "statusCode": 500,
            "body": f"Server error: {str(e)}",
        }
        print(f"{response=}")
        return response


load_controllers()
