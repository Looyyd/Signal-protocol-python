import sys, os

sys.path.append("../")

from crypto.aes import *
from secrets import token_bytes
from crypto.bytearray_operations import xor, to_bytearray

AES_BLOCK_SIZE = 128
AES_BLOCK_SIZE_BYTES = AES_BLOCK_SIZE//8
AES_KEY_SIZE = 256
AES_KEY_SIZE_BYES = AES_KEY_SIZE//8




def cbc_mode_aes_encrypt(plaintext, iv, key):
    if (type(plaintext) == str):
        plaintext = bytearray(plaintext, encoding="utf_8")
    else:
        plaintext = bytearray(plaintext)

    # needs to be a multiple of block size
    # JE laisse les comms pour vérifier les modifs, effacer les coms et les prints plus tard
    # Ici on print les infos avant traitement
    #print("OLD BYTEARRAY : ", plaintext)
    #print(type(plaintext))
    #print(len(plaintext))
    #print(AES_BLOCK_SIZE_BYTES)
    #assert(len(plaintext) % (AES_BLOCK_SIZE_BYTES) ==0) | A apres traitement eventuellement
    # On dectecte si la longueur du texte est un multiple du block size
    MOD = len(plaintext) % (AES_BLOCK_SIZE_BYTES)
    if MOD == 0:
        # Si oui, aucun probleme
        size = len(plaintext) // (AES_BLOCK_SIZE_BYTES)
    else:
        # Si non, on AJOUTE PAR DEFAUT UN BLOC
        size = (len(plaintext) // (AES_BLOCK_SIZE_BYTES)) + 1
    # De cette façon, on peut calculer le pad a ajouter
    PAD = size*AES_BLOCK_SIZE_BYTES % len(plaintext)
    # On fait une boucle for puisqu'on connait la longueur a ajouter
    for i in range (PAD):
        plaintext.append(0)
    # On obtient ici notre nouvel array 
    #print("NEW BYTEARRAY : ", plaintext)
    #print(type(plaintext))
    #print(len(plaintext))
    # Infos remanentes sur le nb de bloc et le padding
    #print("Number of Block : ", size)
    #print("PADDING : ", PAD)
    previous_ct = iv
    output = bytearray()
    for i in range(0, size):
        bloc = xor(previous_ct, plaintext[i*(AES_BLOCK_SIZE_BYTES):(i+1) * (AES_BLOCK_SIZE_BYTES)])
        ct = aes(bloc, key)
        output.extend(ct)
        previous_ct = ct

    return output

def cbc_mode_aes_decrypt(ciphertext, iv, key):
    ciphertext = to_bytearray(ciphertext)
    assert (len(ciphertext) % (AES_BLOCK_SIZE_BYTES) == 0)
    #print("TAILLE CIPHERTEXT")
    #print(len(ciphertext))
    size = len(ciphertext) // (AES_BLOCK_SIZE_BYTES)

    previous_ct = iv
    plaintext= bytearray()

    for i in range(0, size):
        bloc= ciphertext[i*(AES_BLOCK_SIZE_BYTES):(i+1) * (AES_BLOCK_SIZE_BYTES)]
        plaintext.extend(xor(previous_ct, inv_aes(bloc, key)))
        previous_ct = bloc

    #print("DECRYPTED : ", plaintext)
    #print(type(plaintext))
    #Faire traitement sur plaintext ici
    for i in reversed(plaintext):
        if i == 0:
            plaintext.pop()
        else:
            break
    #print("NEW DECRYPTED : ", plaintext)

    return plaintext

def read_file(file: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, file)

    with open(file_path) as f:
        lines = f.readlines()

    plaintext = lines
    plaintext = str(plaintext)
    return plaintext

if __name__ == "__main__":

    plaintext = read_file("../file.txt")
    iv = token_bytes(AES_BLOCK_SIZE_BYTES)
    key = token_bytes(aes.AES_KEY_SIZE_BYTES)

    ct = cbc_mode_aes_encrypt(plaintext, iv, key)
    decrypted = cbc_mode_aes_decrypt(ct,iv, key)

    #print("CT = ", ct)
    print("Decrypted =", decrypted)
    print("Plaintext =", to_bytearray((plaintext)))
    #print(len(plaintext))
    #print(len(ct))
    print("DECRYPTED LEN : ", len(decrypted))
    #print(len(iv))
    #print(len(key))