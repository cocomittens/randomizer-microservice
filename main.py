import json
import os
import random
from typing import Any, List, Tuple

import zmq


DEFAULT_ENDPOINT = os.environ.get("RANDOMIZER_ENDPOINT", "tcp://*:5143")


def select_random_items(input_arr: Any, num_items: int = 1) -> List[Any]:

    if input_arr is None:
        raise ValueError("Request must include an 'items' array.")

    if not isinstance(input_arr, list):
        raise ValueError("Items must be provided as a list.")

    if not input_arr:
        raise ValueError("The items list cannot be empty.")

    if num_items is None:
        num_items = 1

    if not isinstance(num_items, int) or num_items <= 0:
        raise ValueError("Requested selection count must be a positive integer.")

    if not all(isinstance(item, (str, int)) for item in input_arr):
        raise ValueError("Each item must be either an integer or a string.")

    selection_size = min(num_items, len(input_arr))
    return random.sample(input_arr, selection_size)


def create_socket(endpoint: str) -> Tuple[zmq.Context, zmq.Socket]:
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(endpoint)
    return context, socket


def main() -> None:
    endpoint = DEFAULT_ENDPOINT
    context = None
    socket = None
    request_count = 0

    try:
        context, socket = create_socket(endpoint)
        print("=" * 50)
        print("Randomizer service ready")
        print(f"Listening on: {endpoint}")
        print("=" * 50)

        while True:
            message = socket.recv_string()
            request_count += 1

            print(f"[Request #{request_count}] Received: {message}")

            try:
                request = json.loads(message)

                items = request.get("items")
                requested_count = request.get("count", 1)
                selected_items = select_random_items(items, requested_count)

                actual_count = len(selected_items)

                selection_payload = (
                    selected_items[0] if actual_count == 1 else selected_items
                )

                response = {
                    "valid": True,
                    "requested_count": requested_count,
                    "selection": selection_payload,
                    "selection_count": actual_count,
                    "total_items": len(items),
                }

                response_json = json.dumps(response)
                socket.send_string(response_json)

                print(f"[Request #{request_count}] Sent: {response_json}")
                print()

            except json.JSONDecodeError as e:
                error_response = {
                    "valid": False,
                    "error": f"Invalid JSON: {str(e)}",
                }
                socket.send_string(json.dumps(error_response))
                print(f"[Request #{request_count}] Error: Invalid JSON")
                print()

            except ValueError as e:
                error_response = {
                    "valid": False,
                    "error": str(e),
                }
                socket.send_string(json.dumps(error_response))
                print(f"[Request #{request_count}] Error: {str(e)}")
                print()

            except Exception as e:
                error_response = {
                    "valid": False,
                    "error": f"Server error: {str(e)}",
                }
                socket.send_string(json.dumps(error_response))
                print(f"[Request #{request_count}] Error: {str(e)}")
                print()

    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("Shutting down Randomizer service...")
        print(f"Total requests processed: {request_count}")
        print("=" * 50)

    finally:
        if socket is not None:
            socket.close(0)
        if context is not None:
            context.term()


if __name__ == "__main__":
    main()
