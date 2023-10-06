# Chat App

This is our free time project. It's chat application that uses WebSocket protocol (using [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/)) to accomplish communication between users and provide real time chat experience.

Authentication is based on [JWT](https://jwt.io/). For training purposes, only hashing libraries was used to manipulate with tokens (such as PyJWT). Token handling was developed by the author.

Dynamic frontend content is rendered by [Jinja](https://jinja.palletsprojects.com/en/3.1.x/), which is a default Flask template engine. You can notice a bit strange structure of the backend. Every endpoint function, that renders a template, calls API endpoint. This API is a also part of application, so question is, why using `requests` to send request to the same server. Let me explain those approaches.

## Backend structure
Backend consists of two main parts (blueprints):
- auth
- api

You can think of these two parts as standard REST APIs, that returns JSON responsees. Blueprint `auth` contains all routes and utilities that are required for handling user authentication. Meanwhile `api` is taking care of all other operations.\
Than we have `application/views.py` module to render all templates. Routes in this module communicates with `api` and `auth` backend to obtain all necessary permissions and content in order to render required template. This approach was chosen, because first idea with this project was to completely separate backend and frontend. You can take `views.py` module more to the frontend side. It is possible to replace this part with some other framework like React or Vue.js. In that case, Jinja rendering would not be needed and those frontend frameworks could directly comunicate with backend (`auth` and `api`). Simply said, idea was to separate backend and frontend of application.

### Possible solution
Part of `views.py` with sending `requests` to backend could alternatively be replaced with following approach. It's possible to directly access `api`'s or `auth`'s `service` module, that can provide all needed functionality. In this case you need to think more about how to handle authentication. With requests this is handled by `api.controller` and `auth.controller` module, which you are trying avoid. \
Pros of access service directly from `views` instead of sending requests:
- application will be probably faster

Cons:
- `views` module is bound to backend `service`s, which means that frontend would be bound to one specific backend and we cannot approach them as two different services. 

## Token handling
Tokens are stored in `httpOnly` cookies. They are not accessible from JavaScript. Only backend manipulates with token cookies.

## First steps

> __Note:__ following steps will be described for Linux/MacOS. When using Windows, find equivalent commands, or use provided `docker-compose`.

### Running on localhost
> Required Python version: 3.10+
1. Clone the project from Github
```bash
git clone https://github.com/pepab0t/ChatApp.git
```
2. Change directory to project root
```bash
cd /path/to/ChatApp
```
3. Create virutal environment
```bash
python3 -m venv venv

# alternative:
virtualenv venv
```
4. Activate `venv` 
```bash
source ./venv/bin/activate
```
5. Install Python dependencies
```bash
pip install -r requirements.txt
```
6. Open file `main.py` and decide whether to run on Debug mode.
```python
# change debug=False if you want
socketio.run(app, host="127.0.0.1", port=8000, debug=True)
```
> __Note:__ Debug mode means, that server restarts everytime, if you make changes in code.

7. Specify all environment variables. For this, you need to create `.env` file in root directory. Sample is `.env_example`.
In `.env` file, specify following variables:
```bash
APP_SECRET_KEY=
APP_JWT_SECRET=
ACCESS_TOKEN_DURATION_MINS=
ACCESS_TOKEN_TOLERANCE_MINS=
REFRESH_TOKEN_DURATION_HOURS=
DB_URI=
```
> __Tip:__ If you want to use SQLite database, set variable `DB_URI=sqlite:///database.db` for example.

8. Run the application with
```bash
python3 main.py
```

### Run using Docker
1. Follow step 1. and 2. from previous tutorial
2. Download `Docker`, `docker-compose`
3. Open example file `docker-compose.yml` and configure your environment variables.
4. Run command to initialize docker containers:
```bash
docker-compose up -d
```

## Bugs
If you find any bugs, please contact the [author](https://github.com/pepab0t).\
Or feel free to contribute :).