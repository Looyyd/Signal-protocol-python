# flask will be used for the REST API
import flask



# This package contains functions needed by a signal server



class server:
    def __init__(self):
        return

    # The server needs to be able to store keys bundles frm an id
    def store_key_bundle(self, keys, id):
        return

    # The server needs to be able to send the key bundle to someone requesting it
    def send_key_bundle(self, from_id):
        return

    # the server needs to be able to store messages destined to an id
    def store_messages(self, messages, from_id):
        return

    # The server needs to be able to send messages that it stored and are destined to an id
    # the function sends nothing if no messages are destined to this id
    def send_messages(self, to_id):
        return


