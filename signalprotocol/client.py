# resquests will be used to make API calls
import requests
import os


# This package contains the functions needed by a signal client



class client:
    id = None
    # for now server will be on same host
    server_ip = "127.0.0.1"
    server_port = 5000
    def __init__(self, id):
        #id should be an unique identifier, TODO to be determined exactly how it looks
        self.id = id

    #The client needs to be able to register to the server, ie send their key bundle to the server
    def register(self):
        self.send_key_bundle()
        return

    def send_key_bundle(self):
        return


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
    to_id = 2
    #print return code
    print(client1.send_message(to_id,message))

    id_client2 = 2
    client2 = client(id_client2)
    messages = client2.request_messages()
    print(messages)