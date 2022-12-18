# This is a flask app that can be used as the server that the clients will communicate to
# app.py
from flask import Flask, request, jsonify
from signalprotocol import server

app = Flask(__name__)


# Create backend class
server = server.server()

# to send a message
@app.post("/message")
def get_countries():
    return

#to receive the messages destined to you
@app.get("/message")
def add_country():
    if request.is_json:
        return
    return {"error": "Request must be JSON"}, 415


# to register
@app.post("/register")
def register():
    if request.is_json:
        return
    return {"error": "Request must be JSON"}, 415