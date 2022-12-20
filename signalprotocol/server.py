# flask will be used for the REST API
import sqlite3
import json
from random import randrange



# This package contains functions needed by a signal server

SERVER_PORT = 5000

class server:
    #TODO: ajouter un mdp à la database?
    db_name = "signal-db"
    messages_table_name = "messages"
    user_table_name = "users"
    def __init__(self):

        # create database if doesn't exist
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''
                  CREATE TABLE IF NOT EXISTS messages
                  ([message_id] INTEGER PRIMARY KEY, [to_id] INTEGER, [from_id] INTEGER, [message] TEXT)
                  ''')
        c.execute('''
                  CREATE TABLE IF NOT EXISTS users
                  ([user_id] INTEGER PRIMARY KEY, [key_bundle] TEXT)
                  ''')
        conn.commit()

        return

    # The server needs to be able to store keys bundles frm an id
    def store_key_bundle(self, keys, from_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        #TODO: check id is unique,or give back unique id
        sql = "INSERT OR REPLACE INTO users (user_id, key_bundle) VALUES(?,?)"
        args = (from_id, keys)
        c.execute(sql,args)
        conn.commit()
        return

    # The server needs to be able to send the key bundle to someone requesting it
    def send_key_bundle(self, from_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        sql = "SELECT * FROM users where user_id=(?)"
        args = (str(from_id))
        c.execute(sql, args)
        rows = c.fetchall()
        #if empty rows(aka no keys registered) return empty array
        if len(rows)==0:
            #Faudra rajouter les checks pour dans le client
            return json.dumps({})
        else:
            json_string = json.loads(rows[0][1])
            p_one_time_prekeys = json_string["p_one_time_prekeys"]
            # Si pas de prekeys restante
            if len(p_one_time_prekeys) == 0:
                p_one_time_prekey = None
                p_one_time_prekey_n = None
            else:
                p_one_time_prekey_n = randrange(0,len(p_one_time_prekeys))
                p_one_time_prekey = p_one_time_prekeys[p_one_time_prekey_n]
                # remove selected prekey from prekeys
                # would be better if it's deleted only if client receives it
                del p_one_time_prekeys[p_one_time_prekey_n]

            json_string['p_one_time_prekeys'] = p_one_time_prekeys
            #save new keys (minus the chosen one)
            self.store_key_bundle(json.dumps(json_string), from_id)

            # create new string for answer
            del json_string["p_one_time_prekeys"]
            json_string.update({"p_one_time_prekey": p_one_time_prekey, "p_one_time_prekey_n": p_one_time_prekey_n})
        return json.dumps(json_string)

    # the server needs to be able to store messages destined to an id
    def store_message(self, message, from_id, to_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        sql = "INSERT INTO messages (to_id, from_id, message) VALUES(?,?,?)"
        args = (to_id, from_id, message)
        c.execute(sql,args)
        conn.commit()
        return

    # The server needs to be able to send messages that it stored and are destined to an id
    # the function sends nothing if no messages are destined to this id
    def send_messages(self, to_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        sql = "SELECT * FROM messages where to_id=(?)"
        args = (str(to_id))
        c.execute(sql, args)
        rows = c.fetchall()

        # remove the messages afterwards, would be better only if connection succeeds
        sql = "DELETE FROM messages where to_id=(?)"
        cur = conn.cursor()
        cur.execute(sql, (to_id,))
        conn.commit()
        return rows


