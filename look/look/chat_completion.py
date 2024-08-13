import falcon
import json
from connection import TCPClient
import tools as tl

class ChatCompletion:
    def __init__(self, host: str, port: int) -> None:
        self.tcp_client = TCPClient(host, port)
        if not self.tcp_client:
            raise ValueError("Failed to initialize TCPClient")
    
    def on_post(self, req, resp):

        data = req.context.doc

        # Validate required fields in the JSON body
        if 'model' not in data or 'messages' not in data:
            resp.status = falcon.HTTP_400  # Bad Request
            resp.media = {'error': 'Missing required fields: model, messages'}
            return

        # Further validation on the 'messages' array
        if not isinstance(data['messages'], list) or not all('role' in message and 'content' in message for message in data['messages']):
            resp.status = falcon.HTTP_400  # Bad Request
            resp.media = {'error': 'Each message must have a role and content'}
            return

        # Extract the message content to send to the port
        user_message = data.get("messages", [{}])[1].get("content", "")
        if not user_message:
            raise falcon.HTTPBadRequest(description="No user message provided")

        # Parse the received message content
        response_content = self.tcp_client.send_and_wait(user_message).strip()

        # Split the response by null byte and parse each JSON object
        parts = response_content.split('\x00')
        combined_message = ""
        for part in parts:
            if part.strip():
                try:
                    json_part = json.loads(part)
                    combined_message += json_part.get("response", "")
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")

        #print(f"Combined message: {combined_message}")
        
        model=data.get("model","")
        id=tl.generate_chat_id()
        timestamp=tl.generate_created_timestamp()
        system_fp=tl.generate_system_fingerprint(model)
        # Prepare the response
        response_data = {
            "id": id,
            "object": "chat.completion",
            "created": timestamp,
            "model": model,
            "system_fingerprint": system_fp,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": combined_message,
                },
                "logprobs": None,
                "finish_reason": "stop" # parameter has to be given by the inference  
            }],
            "usage": {
                "prompt_tokens": len(user_message),
                "completion_tokens": len(combined_message),
                "total_tokens": len(user_message) + len(combined_message)
            }
        }

        # Set the response media and status
        resp.media = response_data
        resp.status = falcon.HTTP_200
        # Set the response media and status
        resp.media = response_data
        resp.status = falcon.HTTP_200
