from app import create_app
from wsgiref import simple_server

app = create_app()


def main():
    # Run the Falcon app using the built-in WSGI server
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    print("Serving on http://127.0.0.1:8000")
    httpd.serve_forever()

if __name__ == "__main__":
    main()