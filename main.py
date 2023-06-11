from application import create_app, DB_NAME


def main():
    socketio, app = create_app(f"sqlite:///{DB_NAME}")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
