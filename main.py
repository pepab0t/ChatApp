from application import create_app


socketio, app = create_app()


def main():
    socketio.run(app, host="0.0.0.0", port=8000, debug=False)


if __name__ == "__main__":
    main()
