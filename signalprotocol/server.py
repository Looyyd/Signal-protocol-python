# flask will be used for the REST API
import sqlite3



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
    def store_key_bundle(self, keys, id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        #TODO: check id is unique,or give back unique id
        sql = "INSERT INTO users (id, key_bundle) VALUES(?,?)"
        args = (id, keys)
        c.execute(sql,args)
        conn.commit()
        return

    # The server needs to be able to send the key bundle to someone requesting it
    def send_key_bundle(self, from_id):
        return

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
        return rows


