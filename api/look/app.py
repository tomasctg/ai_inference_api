import falcon.asgi
from chat_completion import ChatCompletion
from middleware import *
import asyncio
def create_app(config=None):
    chat_completion = ChatCompletion('localhost', 4200)
    app = falcon.asgi.App(
        middleware=[
            RequireJSON(),
            JSONTranslator(),
        ])
    app.add_route('/v1/chat/completions', chat_completion)
            # Ensure the event loop is created and the task is properly awaited
    return app