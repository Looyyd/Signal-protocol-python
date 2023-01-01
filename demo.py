from signalprotocol.client import *

file_path = "/home/bastien/test-clone-gs15/Signal-protocol-python/crypto/file.txt"

print("----------------------------------------")
print("      Initiliating clients and keys     ")
print("----------------------------------------")
# Creating a client to cummunicate
id_client2 = 2
client2 = client(id_client2)
# Client 2 needs to upload key bundle
client2.register()

# Same operations for Client 1
id_client1 = 1
client1 = client(id_client1)
client1.register()

# To send messages to Client 2, Client 1 retrieves the keys on the server
keys_response = client1.get_key_bundle(client1.id)
to_id = 2

print("----------------------------------------")
print("      Clients and keys initialized      ")
print("----------------------------------------")

# Initializing different types of messages
print("----------------------------------------")
print("            Sending Messages            ")
print("----------------------------------------")
message = "Test message"    
client1.send_message(to_id,message, False)
client1.send_message(to_id,"Message 2", False)
client1.send_message(to_id,file_path, True)
print("----------------------------------------")
print("              Messages Sent             ")
print("----------------------------------------")


# Now Client 2, wants to read his incoming messages, so it retrieves them on the server
print("----------------------------------------")
print("          Requesting messages           ")
print("----------------------------------------")
messages = client2.request_messages()
client2.read_messages(messages)

print("READING ALL MESSSAGES")
client2.read_all_local_message()
print("READING ALL LOCAL FROM ID= 2")
client2.read_local_messages_from(2)
print("----------------------------------------")
print("   Messages read - Process Completed    ")
print("----------------------------------------")

# Testing message in the other direction, it should reuse the already established key chain

print("----------------------------------------")
print("    Testing Back and Forth exchanges    ")
print("----------------------------------------")

print("----------------------------------------")
print("              Client 2 to 1             ")
print("----------------------------------------")
to_id=1
client2.send_message(to_id,"Message other direction", isFile=False)
client2.send_message(to_id,"Second Message other direction", isFile=False)
messages = client1.request_messages()
client1.read_messages(messages)

print("----------------------------------------")
print("              Client 1 to 2             ")
print("----------------------------------------")
to_id=2
client1.send_message(to_id,"Back in first direction, hope this works", isFile=False)
messages = client2.request_messages()
client2.read_messages(messages)

print("----------------------------------------")
print("              Client 2 to 1             ")
print("----------------------------------------")
to_id=1
client2.send_message(to_id,"Changing ratchet key in other direction, inshalla", isFile=False, update_ratchet_key=True)
messages = client1.request_messages()
client1.read_messages(messages)

print("----------------------------------------")
print("              Client 1 to 2             ")
print("----------------------------------------")
to_id=2
client1.send_message(to_id,"Back in first direction after ratchet range. ALLELUIA", isFile=False)
messages = client2.request_messages()
client2.read_messages(messages)
