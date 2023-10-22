from application import create_app


socketio, app = create_app()


def main():
    socketio.run(app, host="127.0.0.1", port=8001, debug=False)


if __name__ == "__main__":
    main()
