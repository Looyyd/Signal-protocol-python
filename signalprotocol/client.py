# resquests will be used to make API calls
import requests
import os
from crypto.diffie_hellman import *
import json
from crypto.hkdf import *
from crypto.counter_mode import *
from crypto.bytearray_operations import *
import sqlite3


# This package contains the functions needed by a signal client


class client:
    id = None
    # for now server will be on same host
    server_ip = "127.0.0.1"
    server_port = 5000
    # TODO: not sure about key size, probably higher since it's DH
    key_size = 256
    identity_key = None
    signed_prekey = None
    prekey_signature = None
    one_time_prekeys = []
    key_bundle = None
    #generate 10 otk
    number_otk = 1

    db_name = None
    def __init__(self, id):
        #id should be an unique identifier, TODO to be determined exactly how it looks
        self.id = id
        self.db_name = "client-" + str(self.id) + ".db"

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
        self.key_bundle = json.dumps(json_string)
        return

    def generate_keys(self):
        # First the client generates by sending:
        # One identity key
        # one signed prekey and it's signature
        # A defined number of prekeys

        self.identity_key = randbits(self.key_size)
        # TODO: add signature
        self.signed_prekey = randbits(self.key_size)
        # generate multiple keys
        self.generate_one_time_keys()

        # Create key bundle
        self.create_bundle()
        return

    def generate_one_time_keys(self):
        for i in range(0,self.number_otk):
            self.one_time_prekeys.append(randbits(self.key_size))


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

    def create_session_key(self, keys_response, ephemeral_key):
        # parse the response for keys
        #row array then second column
        print("keys_response:", keys_response)
        json_string=json.loads(keys_response)
        print("json_keys_string=", json_string)
        p_identity_key = int(json_string["p_identity_key"], 16)
        #TODO: verify signature
        p_signed_prekey = int(json_string["p_signed_prekey"], 16)

        # remember which key was used
        p_one_time_prekey_n = json_string["p_one_time_prekey_n"]

        # Now to the 3 (optionnaly 4 if one time prekey is used) key exchanges
        # 1 The identity key of Alice and the signed prekey of Bob
        dh1 = dh_step2(p_signed_prekey, self.identity_key)
        # 2 The ephemeral key of Alice and the identity key of Bob
        dh2 = dh_step2(p_identity_key, ephemeral_key)
        # 3 The ephemeral key of Alice and the signed prekey of Bob
        dh3 = dh_step2(p_signed_prekey, ephemeral_key)
        # 4 If Bob still has a one-time prekey available, his one-time prekey and the ephem-
        # eral key of Alice
        # dh4 optional
        if (p_one_time_prekey_n != None):
            # take the prekey it gave us
            p_one_time_prekey = int(json_string["p_one_time_prekey"], 16)
            dh4 = dh_step2(p_one_time_prekey, ephemeral_key)
        else:
            dh4 = bytearray()

        # use KDF to get session key
        keys_str = str(dh1) +str(dh2) +str(dh3) +str(dh4)
        keys_str = to_bytearray(keys_str)
        session_key = session_key_derivation(keys_str)
        return session_key



    #The client needs to be able to send a message to an id
    def send_message(self, to_id, message):
        ### Encrypt message
        # get key bundle of destination
        keys_response = self.get_key_bundle(to_id)
        # create ephemeral key
        ephemeral_key = randbits(self.key_size)
        # create session key
        session_key = self.create_session_key(keys_response, ephemeral_key)

        # counter mode encrypt the message with session key
        nonce = token_bytes(16)
        # session key is 512 bits, take half of it
        aes_session_key = session_key[0:AES_KEY_SIZE//8]
        stream = counter_mode_aes(len(message) * 8 // 128 + 1, nonce, aes_session_key)
        # message needs to be a bytearray
        message = to_bytearray(message)
        # stream cipher
        encrypted = xor(message, stream)

        # ephermeral public key generation
        p_ephemeral_key = dh_step1(ephemeral_key)
        p_identity_key = dh_step1(self.identity_key)
        # add the index of the one time key that was used
        json_string=json.loads(keys_response)
        p_one_time_prekey_n = json_string["p_one_time_prekey_n"]

        message_json = {"p_identity_key": hex(p_identity_key),
                        "p_ephemeral_key": hex(p_ephemeral_key),
                        "nonce": nonce.hex(),
                        "p_one_time_prekey_n": p_one_time_prekey_n,
                        "ciphertext": encrypted.hex()}

        #api endpoint is:
        url = "http://" + self.server_ip + ":" + str(self.server_port) + "/message"
        request_json = {"to_id": to_id, "from_id": self.id, "message": json.dumps(message_json)}
        print(message_json)
        print(request_json)
        response = requests.post(url, json=request_json )
        #not sure what to return for now
        return response.status_code

    def read_messages(self,messages):
        for msg in messages:
            print(msg)
            from_id = msg[1]
            txt = msg[3]
            json_message = json.loads(txt)
            print(json_message)
            p_identity_key =  int(json_message["p_identity_key"],16)
            p_ephemeral_key =  int(json_message["p_ephemeral_key"],16)
            nonce = to_bytearray( bytearray.fromhex(json_message["nonce"]))
            ciphertext = to_bytearray( bytearray.fromhex(json_message["ciphertext"]))
            # Now to the 3 (optionnaly 4 if one time prekey is used) key exchanges
            # 1 The identity key of Alice and the signed prekey of Bob
            dh1 = dh_step2(p_identity_key, self.signed_prekey)
            # 2 The ephemeral key of Alice and the identity key of Bob
            dh2 = dh_step2(p_ephemeral_key, self.identity_key)
            # 3 The ephemeral key of Alice and the signed prekey of Bob
            dh3 = dh_step2(p_ephemeral_key, self.signed_prekey)
            # 4 If Bob still has a one-time prekey available, his one-time prekey and the ephem-
            # eral key of Alice
            # use the one time prekey that is indicated
            p_one_time_prekey_n = json_message["p_one_time_prekey_n"]
            if p_one_time_prekey_n==None:
                dh4 = bytearray()
                # should generate more one time keys and send them to server
                self.generate_one_time_keys()
                self.create_bundle()
                self.send_key_bundle()
            else:
                one_time_prekey_used = self.one_time_prekeys[p_one_time_prekey_n]
                dh4 = dh_step2(p_ephemeral_key, one_time_prekey_used)
                # remove the one time prekey
                # il y aura un problème avec ce système si un autre client demande un clé mais ne l'utilise finalement pas
                # peut etre qu'il faudrai que la partie publique de DH de la one time key soit envoyé aussi
                # comme ca on peut verifier que c'est bien la bonne clé qu'on utilise et qu'aucune erreur est survenu
                del self.one_time_prekeys[p_one_time_prekey_n]

            # use KDF to get session key
            keys_str = str(dh1) +str(dh2) +str(dh3) +str(dh4)
            keys_str = to_bytearray(keys_str)
            session_key = session_key_derivation(keys_str)
            aes_session_key = session_key[0:AES_KEY_SIZE//8]
            stream = counter_mode_aes(len(ciphertext) * 8 // 128 + 1, nonce, aes_session_key)
            # message needs to be a bytearray
            ciphertext = to_bytearray(ciphertext)
            # stream cipher
            decrypted = xor(ciphertext, stream)
            print("Message from id ", from_id, ": ", decrypted)
            #  add to local database
            self.add_message_to_local_db(decrypted, from_id)

    def add_message_to_local_db(self, message, from_id):
        # create database if it doesn't exist
        self.create_local_db()

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # append the message to the database
        sql = "INSERT INTO messages (from_id, message) VALUES(?,?)"
        args = (from_id, message)
        c.execute(sql,args)

        # commit changes
        conn.commit()
        return

    def create_local_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''
                          CREATE TABLE IF NOT EXISTS messages
                          ([message_id] INTEGER PRIMARY KEY, [from_id] INTEGER, [message] TEXT)
                          ''')
        return


    def read_local_messages_from(self, from_id):
        #create if doesn't exist
        self.create_local_db()
        # print all messages from local database
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        sql = "SELECT * FROM messages WHERE from_id=(?)"
        args = (from_id,)
        c.execute(sql, args)

        rows = c.fetchall()
        for row in rows:
            # 1 is row id
            from_id = row[1]
            message = row[2]
            print("Message from ", from_id, ": ", message)
        return

    def read_all_local_message(self):

        #create if doesn't exist
        self.create_local_db()
        # print all messages from local database
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        sql = "SELECT * FROM messages"
        c.execute(sql)

        rows = c.fetchall()
        for row in rows:
            # 1 is row id
            from_id = row[1]
            message = row[2]
            print("Message from ", from_id, ": ", message)
        return
    # The client needs to be able to send files
    def send_file(self, to_id):
        return



    #testing
if __name__ == "__main__":
    # TODO launch the flask api, do it manually meanwhile
    #os.environ['FLASK_APP'] = "server-app.py"
    #os.environ['FLASK_ENV'] = 'development'
    #os.system("flask run")


    id_client2 = 2
    client2 = client(id_client2)
    #client2 needs to upload key bundle
    client2.register()

    id_client1 = 1
    client1 = client(id_client1)
    message = "Test message"
    client1.register()
    keys_response = client1.get_key_bundle(client1.id)
    print(keys_response)
    to_id = 2
    #print return code
    print(client1.send_message(to_id,message))
    print(client1.send_message(to_id,"Message 2"))
    print(client1.send_message(to_id,"Message 3"))


    messages = client2.request_messages()
    print(messages)
    client2.read_messages(messages)

    print("READIN ALL MESSSAGES")
    client2.read_all_local_message()
    print("READING ALL LOCAL FROM ID= 2")
    client2.read_local_messages_from(2)