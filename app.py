import falcon
import json
import subprocess
from wsgiref import simple_server


class RequireJSON:
    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                description='This API only supports responses encoded as JSON.',
                href='http://docs.examples.com/api/json',
            )

        if req.method in ('POST', 'PUT'):
            if 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    title='This API only supports requests encoded as JSON.',
                    href='http://docs.examples.com/api/json',
                )

class JSONTranslator:
    # NOTE: Normally you would simply use req.media and resp.media for
    # this particular use case; this example serves only to illustrate
    # what is possible.

    def process_request(self, req, resp):
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes from the request body.
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Nothing to do
            return

        body = req.bounded_stream.read()
        if not body:
            raise falcon.HTTPBadRequest(
                title='Empty request body',
                description='A valid JSON document is required.',
            )

        try:
            req.context.doc = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            description = (
                'Could not decode the request body. The '
                'JSON was incorrect or not encoded as '
                'UTF-8.'
            )

            raise falcon.HTTPBadRequest(title='Malformed JSON', description=description)

    def process_response(self, req, resp, resource, req_succeeded):
        if not hasattr(resp.context, 'result'):
            return

        resp.text = json.dumps(resp.context.result)


class ChatCompletionResource:
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
            
            # Parse the incoming request
            

            # Extract the message content to send to the port
            user_message = data.get("messages", [{}])[1].get("content", "")
            if not user_message:
                raise falcon.HTTPBadRequest(description="No user message provided")

            # Prepare the command to send the message to the port using netcat
            byte_message = f"{user_message}\x00".encode('utf-8')
            print(f"Byte message to send: {byte_message}")
            try:
                # Execute the netcat command
                process = subprocess.Popen(
                    ['netcat', 'localhost', '4200'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = process.communicate(input=byte_message)


                if process.returncode != 0:
                    raise falcon.HTTPInternalServerError(description=f"Error communicating with port: {stderr.decode('utf-8')}")

                # Parse the received message content
                response_content = stdout.decode('utf-8').strip()
                print(f"Raw response content: {response_content}")

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

                print(f"Combined message: {combined_message}")

                # Prepare the response
                response_data = {
                    "id": "chatcmpl-123",
                    "object": "chat.completion",
                    "created": 1677652288,
                    "model": "gpt-4o-mini",
                    "system_fingerprint": "fp_44709d6fcb",
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": combined_message,
                        },
                        "logprobs": None,
                        "finish_reason": "stop"
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
            except subprocess.CalledProcessError as e:
                raise falcon.HTTPInternalServerError(description=f"Subprocess error: {str(e)}")


# Initialize Falcon API and add route
app = falcon.App(    
        middleware=[
        RequireJSON(),
        JSONTranslator(),
    ])
chat_completion = ChatCompletionResource()
app.add_route('/v1/chat/completions', chat_completion)

# For running with a WSGI server like Gunicorn
# You would run it with: gunicorn 'app:app'
# Main function for debugging
def main():
    # Run the Falcon app using the built-in WSGI server
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    print("Serving on http://127.0.0.1:8000")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
    
    



# The app instance is an ASGI callable
# app = falcon.asgi.App(

# )

# db = StorageEngine()
# things = ThingsResource(db)
# app.add_route('/{user_id}/things', things)

# # If a responder ever raises an instance of StorageError, pass control to
# # the given handler.
# app.add_error_handler(StorageError, StorageError.handle)

# # Proxy some things to another service; this example shows how you might
# # send parts of an API off to a legacy system that hasn't been upgraded
# # yet, or perhaps is a single cluster that all data centers have to share.
# sink = SinkAdapter()
# app.add_sink(sink, r'/search/(?P<engine>ddg|y)\Z')