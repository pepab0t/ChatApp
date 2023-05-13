from application import create_socketio


def main():
    socketio, app = create_socketio()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
