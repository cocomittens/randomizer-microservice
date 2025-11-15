import zmq
import json

def handle_request(request):
    request_1 = {}
    request_json = json.dumps(request)
    socket.send_string(request_json)
    response_json = socket.recv_string()
    response = json.loads(response_json)
    return response


def handle_response(response):
    if response["valid"]:
        print(f"""Requested count: {response["requested_count"]}, 
              Selection: {response["selection"]}, 
              Selection Count: {response["selection_count"]}, 
              Total items: {response["total_items"]}""")
    else:
        print(f"Validation error: {response['error']}")


context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5143")

request_1 = {"items": ["cats", "dogs", "bunnies"]}
request_2 = {"items": [1, 2, 3, 4, 5], "count": 1}
request_3 = {"items": [1, 2, 3, 4, 5], "count": 2}

response_1 = handle_request(request_1)
response_2 = handle_request(request_2)
response_3 = handle_request(request_3)

handle_response(response_1)
handle_response(response_2)
handle_response(response_3)
socket.close()
context.term()