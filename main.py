from application import create_app


socketio, app = create_app()


def main():
    socketio.run(app, host="127.0.0.1", port=8000, debug=True)


if __name__ == "__main__":
    main()
