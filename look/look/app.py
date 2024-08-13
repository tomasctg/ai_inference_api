import falcon
from chat_completion import ChatCompletion
from middleware import *


def create_app(config=None):
    chat_completion = ChatCompletion('localhost', 4200)
    app = falcon.App(
        middleware=[
            RequireJSON(),
            JSONTranslator(),
        ])
    app.add_route('/v1/chat/completions', chat_completion)

    return app
