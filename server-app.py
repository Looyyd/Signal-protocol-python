# This is a flask app that can be used as the server that the clients will communicate to
# app.py
from flask import Flask, request, jsonify
from signalprotocol import server
import json

app = Flask(__name__)


# Create backend class
server = server.server()

# to send a message
@app.post("/message")
def send_message():
    if request.is_json:
        json_message = request.get_json()
        #TODO ajouter try except
        to_id = json_message["to_id"]
        from_id = json_message["from_id"]
        message = json_message["message"]
        server.store_message(message, from_id, to_id)

        return jsonify(success=True)
    return {"error": "Request must be JSON"}, 415

#to receive the messages destined to you
@app.get("/message")
def receive_message():
    if request.is_json:
        json_message = request.get_json()
        to_id = json_message["to_id"]
        rows = server.send_messages(to_id)
        jsonRows = json.dumps(rows)
        return jsonRows, 200
    return {"error": "Request must be JSON"}, 415


# to register
@app.post("/register")
def register():
    if request.is_json:
        return
    return {"error": "Request must be JSON"}, 415