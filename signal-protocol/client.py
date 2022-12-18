

# This package contains the functions needed by a signal client



class client:
    id = None
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
        return


    #The client needs to be able to send a message to an id
    def send_message(self, to_id):
        return

    # The client needs to be able to send files
    def send_file(self, to_id):
        return