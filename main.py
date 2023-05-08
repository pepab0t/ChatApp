from application import create_app, create_socketio


def main():
    app = create_app()
    socketio = create_socketio(app)

    socketio.run(app, host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
