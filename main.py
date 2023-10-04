from application import create_app


def main():
    socketio, app = create_app()
    socketio.run(
        app, host="127.0.0.1", port=8000, debug=False, allow_unsafe_werkzeug=True
    )


if __name__ == "__main__":
    main()
