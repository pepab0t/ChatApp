from application import DB_NAME, create_app


def main():
    socketio, app = create_app(f"sqlite:///{DB_NAME}")
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)


if __name__ == "__main__":
    main()
