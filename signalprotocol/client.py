# resquests will be used to make API calls
import requests
import os
from crypto.diffie_hellman import *
import json
from crypto.hkdf import *
from crypto.counter_mode import *
from crypto.bytearray_operations import *
import sqlite3
import binascii


# This package contains the functions needed by a signal client


class client:
    id = None
    # for now server will be on same host
    server_ip = "127.0.0.1"
    server_port = 5000
    # key_size of DH key exchange
    dh_key_size = 2048
    identity_key = None
    signed_prekey = None
    # TODO: add signature
    prekey_signature = None
    one_time_prekeys = []
    key_bundle = None
    #number of one time keys generated
    number_otk = 1

    db_name = None
    def __init__(self, id):
        #id should be an unique identifier
        self.id = id
        self.db_name = "client-" + str(self.id) + ".db"
        # create local db at init
        self.create_local_db()

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

        self.identity_key = randbits(self.dh_key_size)
        # TODO: add signature
        self.signed_prekey = randbits(self.dh_key_size)
        # generate multiple keys
        self.generate_one_time_keys()

        # Create key bundle
        self.create_bundle()
        return

    def generate_ratchet_key(self):
        # TODO: comment genrere des clefs pour dh?
        return hex(randbits(self.dh_key_size))

    def generate_one_time_keys(self):
        for i in range(0,self.number_otk):
            self.one_time_prekeys.append(randbits(self.dh_key_size))


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

    def create_root_key_when_sending(self, keys_response, ephemeral_key):
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
        root_key = session_key_derivation(keys_str)
        return root_key

    def keys_response_get_signed_prekey(self, keys_response):
        json_string=json.loads(keys_response)
        #TODO: verify signature
        p_signed_prekey = int(json_string["p_signed_prekey"], 16)
        return p_signed_prekey

    def table_row_to_key_chains(self, row):
        #      sending    receiving   root       p_ratchet  my_ratchet  excpecting ratchet
        return row[0][1], row[0][2],  row[0][3], row[0][4], row[0][5],  row[0][6]

    #The client needs to be able to send a message to an id
    def send_message(self, to_id, message, update_ratchet_key=False):
        ### Encrypt message
        #Check if sessions key exists
        rows = self.get_local_session_keys_from_db(to_id)
        print("ROWS = ", rows)

        if len(rows)==0:
            # New destination
            no_session_key = True
        else:
            # Already known destinatino
            no_session_key = False
        # if no session key already
        if no_session_key:
            # generate new key
            my_ratchet_key = self.generate_ratchet_key()
            # we expect new ratchet from the destination since we don't have one for now
            expecting_new_ratchet = True
            # We don't know his key
            p_ratchet_key = ""

            # get key bundle of destination
            keys_response = self.get_key_bundle(to_id)
            # create ephemeral key
            ephemeral_key = randbits(self.dh_key_size)
            # create root key
            root_key = self.create_root_key_when_sending(keys_response, ephemeral_key)

            # create ratchet key
            # when no session, use public signed key
            p_presigned_key = self.keys_response_get_signed_prekey(keys_response)
            ratchet_DH = dh_step2(p_presigned_key, int(my_ratchet_key, 16))

            # first derivation creates key chains
            derivation_input = root_key + to_bytearray(hex(ratchet_DH))
            root_key_chain, sending_key_chain = chain_keys_kdf(derivation_input)

            # 1 KDF to get the encryption key to send message
            sending_key_chain, encryption_key = chain_keys_kdf(sending_key_chain)

            #receiving key is empty for now
            receiving_key_chain = bytearray()


        else :
            #if there are keychains already
            sending_key_chain, receiving_key_chain, root_key_chain,\
                p_ratchet_key, my_ratchet_key, expecting_new_ratchet= self.table_row_to_key_chains(rows)

            print("ROWS WHEN SENDING")
            print(rows)
            if len(sending_key_chain) == 0 or update_ratchet_key==True:
                # we need to generate new key chains
                # because we received somthing using our presigned key only
                # OR BECAUSE we just want to update the ratchet key

                # 1 KDF with root key to create the chain
                my_ratchet_key = self.generate_ratchet_key()
                ratchet_DH = dh_step2(int(p_ratchet_key, 16), int(my_ratchet_key, 16))
                # update the root key chain with the new ratchet
                kdf_input = root_key_chain + to_bytearray(hex(ratchet_DH))
                # update sending key chain first
                root_key_chain, sending_key_chain = chain_keys_kdf(kdf_input)
                # update receiving key chain second
                kdf_input = root_key_chain + to_bytearray(hex(ratchet_DH))
                root_key_chain, receiving_key_chain = chain_keys_kdf(kdf_input)

            ## generate new ratchet if asked
            #if update_ratchet_key == True:
                ## 1 KDF with root key to create the chain
                #my_ratchet_key = self.generate_ratchet_key()
                #ratchet_DH = dh_step2(p_ratchet_key,my_ratchet_key)
                ## update the root key chain with the new ratchet
                #kdf_input = root_key_chain + to_bytearray(hex(ratchet_DH))
                ## update sending key chain first
                #root_key_chain, sending_key_chain = chain_keys_kdf(kdf_input)
                ## update receiving key chain second
                #kdf_input = root_key_chain + to_bytearray(hex(ratchet_DH))
                #root_key_chain, receiving_key_chain = chain_keys_kdf(kdf_input)


            # 1 KDF to get the encryption key for this message
            sending_key_chain, encryption_key = chain_keys_kdf(sending_key_chain)

        #update chain value
        self.update_sessions_keys_in_local_db(to_id,sending_key_chain, receiving_key_chain, root_key_chain,
                                              p_ratchet_key, my_ratchet_key, expecting_new_ratchet)

        # counter mode encrypt the message with session key
        nonce = token_bytes(16)
        # session key is 512 bits, take half of it
        aes_session_key = encryption_key[0:AES_KEY_SIZE//8]
        stream = counter_mode_aes(len(message) * 8 // 128 + 1, nonce, aes_session_key)
        # message needs to be a bytearray
        message = to_bytearray(message)
        # stream cipher
        encrypted = xor(message, stream)

        if no_session_key:
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
                            "ciphertext": encrypted.hex(),
                            "p_ratchet_key": hex(dh_step1(int(my_ratchet_key,16)))
                            }
        else:
            #there is a session key already
            message_json={"nonce": nonce.hex(),
                          "ciphertext": encrypted.hex(),
                          "p_ratchet_key": hex(dh_step1(int(my_ratchet_key,16)))
            }

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
            from_id = msg[2]
            print("WHILE READING from id is:", from_id)
            print("MESSAGE IS:", msg)
            txt = msg[3]
            json_message = json.loads(txt)
            nonce = to_bytearray( bytearray.fromhex(json_message["nonce"]))
            ciphertext = to_bytearray( bytearray.fromhex(json_message["ciphertext"]))

            # TODO : delete this it's useless in the end
            expecting_ratchet = False
            # check if session_key_already exists
            rows = self.get_local_session_keys_from_db(from_id)
            print(rows)
            if (len(rows)==0):
                # create the key chains

                p_ratchet_key =  json_message["p_ratchet_key"]
                # generate our own ratchet key
                my_ratchet_key =  self.generate_ratchet_key()

                p_identity_key =  int(json_message["p_identity_key"],16)
                p_ephemeral_key =  int(json_message["p_ephemeral_key"],16)
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

                # last key is optional
                if p_one_time_prekey_n==None:
                    # if key isn't there, add nothing to dh4
                    dh4 = bytearray()
                    # generate more one time keys and send them to server
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
                # The first key is a result of all the DH exchanges
                root_key = session_key_derivation(keys_str)

                # calculate ratchet data to calculate key chain
                # When first receiving, we use our private presigned key and the advertised ratchet key
                ratchet_DH = dh_step2(int(p_ratchet_key,16), self.signed_prekey)

                # The first key derivation creates the receiving key
                derivation_input = root_key + to_bytearray(hex(ratchet_DH))
                root_key_chain , receiving_key_chain = chain_keys_kdf(derivation_input)

                # 1 KDF to get encryption key for this message
                receiving_key_chain, encryption_key = chain_keys_kdf(receiving_key_chain)

                #sending key chain is empty for now
                sending_key_chain = bytearray()

            else:
                # if key chains exist already
                sending_key_chain, receiving_key_chain, root_key_chain,\
                    p_ratchet_key_memory, my_ratchet_key, expecting_ratchet= self.table_row_to_key_chains(rows)


                p_ratchet_key = json_message["p_ratchet_key"]

                print("Ratchet in memory :", p_ratchet_key_memory)
                print("Ratchet received : ", p_ratchet_key)

                # check if ratchet  key has change
                if (p_ratchet_key != p_ratchet_key_memory):
                    print("RATCHET KEY HAS CHANGED")
                    DH_ratchet = dh_step2(int(p_ratchet_key,16), int(my_ratchet_key,16))
                    kdf_input = root_key_chain + to_bytearray(hex(DH_ratchet))
                    # update receiving key
                    root_key_chain, receiving_key_chain = chain_keys_kdf(kdf_input)
                    # update sending key chain
                    # TODO : ne pas oublier de lire les messages avant de changer les keychains définitivement
                    # c'est un problème si on recoit des trucs out of order mais ca n'arrivera pas dans nos tests

                    kdf_input = root_key_chain + to_bytearray(hex(DH_ratchet))
                    root_key_chain, sending_key_chain = chain_keys_kdf(kdf_input)

                # not needed anymore since the ratchet_key will change if the keychain is null
                #if len(receiving_key_chain) == 0:
                    ##create key chain with root key
                    #root_key_chain, receiving_key_chain = chain_keys_kdf(root_key_chain)

                # 1 KDF to get decryption key for this message
                receiving_key_chain, encryption_key = chain_keys_kdf(receiving_key_chain)

            # instert into local db either way( if key chain exists or not)
            self.update_sessions_keys_in_local_db(from_id, sending_key_chain, receiving_key_chain, root_key_chain,
                                                  p_ratchet_key, my_ratchet_key, expecting_ratchet)

            aes_session_key = encryption_key
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

    #returns row of database corresponding to form_id, returns empty row if not in db
    def get_local_session_keys_from_db(self, from_id):
        print("GETTING key with id", from_id )
        #create if doesn't exist
        self.create_local_db()
        # print all messages from local database
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        sql = "SELECT * FROM session_keys WHERE id=(?)"
        args = (from_id,)
        c.execute(sql, args)

        rows = c.fetchall()
        return rows

    def update_sessions_keys_in_local_db\
                    (self, id, sending_key_chain, receiving_key_chain, root_key_chain,
                     p_ratchet_key, my_ratchet_key, expecting_new_ratchet):
        print("UPDATING key with id", id )
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        #update aka insert or replace
        sql = "INSERT OR REPLACE INTO session_keys " \
              "(id, sending_key, receiving_key, root_key, p_ratchet_key, my_ratchet_key, expecting_new_ratchet)" \
              "VALUES(?,?,?,?,?,?,?)"
        args = (id, sending_key_chain, receiving_key_chain, root_key_chain,
                p_ratchet_key, my_ratchet_key, expecting_new_ratchet)
        c.execute(sql,args)
        conn.commit()

    def create_local_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''
                          CREATE TABLE IF NOT EXISTS messages
                          ([message_id] INTEGER PRIMARY KEY,
                           [from_id] INTEGER,
                            [message] TEXT)
                          ''')
        # create table of key chain
        c.execute('''
                          CREATE TABLE IF NOT EXISTS session_keys
                          ([id] INTEGER PRIMARY KEY,
                          [sending_key] TEXT,
                           [receiving_key] TEXT,
                            [root_key] TEXT,
                             [p_ratchet_key] TEXT,
                              [my_ratchet_key] TEXT,
                               [expecting_new_ratchet] BOOLEAN)
                          ''')
        conn.commit()
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
            # index 0 is row id
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
    to_id = 2
    #print return code
    client1.send_message(to_id,message)
    client1.send_message(to_id,"Message 2")
    client1.send_message(to_id,"Message 3")


    messages = client2.request_messages()
    client2.read_messages(messages)

    print("READIN ALL MESSSAGES")
    client2.read_all_local_message()
    print("READING ALL LOCAL FROM ID= 2")
    client2.read_local_messages_from(2)

    # Testing message in the other direction, it should reuse the already established key chain
    to_id=1
    client2.send_message(to_id,"Message other direction")
    client2.send_message(to_id,"Second Message other direction")
    messages = client1.request_messages()
    client1.read_messages(messages)

    to_id=2
    client1.send_message(to_id,"Back in first direction, hope this works")
    messages = client2.request_messages()
    client2.read_messages(messages)

    to_id=1
    client2.send_message(to_id,"Changing ratchet key in other direction, inshalla", update_ratchet_key=True)
    messages = client1.request_messages()
    client1.read_messages(messages)


    to_id=2
    client1.send_message(to_id,"Back in first direction after ratchet range. ALLELUIA")
    messages = client2.request_messages()
    client2.read_messages(messages)

