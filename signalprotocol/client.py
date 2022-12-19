# resquests will be used to make API calls
import requests
import os
from crypto.diffie_hellman import *


# This package contains the functions needed by a signal client

def read_messages(messages):
    for msg in messages:
        from_id = msg[1]
        txt = msg[3]
        print("Message from id ", from_id, ": ", txt)

class client:
    id = None
    # for now server will be on same host
    server_ip = "127.0.0.1"
    server_port = 5000
    key_size = 256
    identity_key = None
    signed_prekey = None
    prekey_signature = None
    one_time_prekeys = []
    key_bundle = None
    def __init__(self, id):
        #id should be an unique identifier, TODO to be determined exactly how it looks
        self.id = id

    #The client needs to be able to register to the server, ie send their key bundle to the server
    def register(self):
        self.generate_keys()
        self.send_key_bundle()
        return

    def create_bundle(self):
        #bundle contains first DH steps of each key
        # p stands for public
        p_identity_key = hex(dh_step1(self.identity_key))
        p_signed_prekey = hex(dh_step1(self.signed_prekey))
        p_one_time_prekeys = []
        for key in self.one_time_prekeys:
            p_one_time_prekeys.append(hex(dh_step1(key)))
        #bundle should be json
        #TODO: add signature to bundle
        json_string = {"p_identity_key": p_identity_key, "p_signed_prekey": p_signed_prekey, "p_one_time_prekeys": p_one_time_prekeys}
        self.key_bundle = str(json_string)
        return

    def generate_keys(self):
        # First the client generates by sending:
        # One identity key
        # one signed prekey and it's signature
        # A defined number of prekeys

        self.identity_key = randbits(self.key_size)
        # TODO: add signature
        self.signed_prekey = randbits(self.key_size)
        self.one_time_prekeys.append(randbits(self.key_size))

        # Create key bundle
        self.create_bundle()
        return


    def send_key_bundle(self):
        #api endpoint is:
        url = "http://" + self.server_ip + ":" + str(self.server_port) + "/keys"
        message_json = {"from_id": self.id, "keys": self.key_bundle}
        response = requests.post(url, json=message_json )
        #not sure what to return for now
        return response.status_code

    def get_key_bundle(self, from_id):
        #api endpoint is:
        url = "http://" + self.server_ip + ":" + str(self.server_port) + "/keys"
        message_json = {"from_id": from_id}
        response = requests.get(url, json=message_json )
        #not sure what to return for now
        #TODO: input validate json to not error when not json is received(which happens when server errors for exemple)
        return response.json()

    # The client needs to be able to request messages that are destined to it
    def request_messages(self):
        #api endpoint is:
        url = "http://" + self.server_ip + ":" + str(self.server_port) + "/message"
        message_json = {"to_id": self.id}
        # get to receive messages
        response = requests.get(url, json=message_json )
        jsonString = response.json()
        #not sure what to return for now
        return jsonString


    #The client needs to be able to send a message to an id
    def send_message(self, to_id, message):
        #api endpoint is:
        url = "http://" + self.server_ip + ":" + str(self.server_port) + "/message"
        message_json = {"to_id": to_id, "from_id": self.id, "message": message}
        response = requests.post(url, json=message_json )
        #not sure what to return for now
        return response.status_code

    # The client needs to be able to send files
    def send_file(self, to_id):
        return



    #testing
if __name__ == "__main__":
    # TODO launch the flask api, do it manually meanwhile
    #os.environ['FLASK_APP'] = "server-app.py"
    #os.environ['FLASK_ENV'] = 'development'
    #os.system("flask run")

    id_client1 = 1
    client1 = client(id_client1)
    message = "Test message"
    client1.register()
    keys = client1.get_key_bundle(client1.id)
    print(keys)
    to_id = 2
    #print return code
    #print(client1.send_message(to_id,message))

    id_client2 = 2
    client2 = client(id_client2)
    messages = client2.request_messages()
    print(messages)
    read_messages(messages)