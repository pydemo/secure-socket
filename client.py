import socket
import os
import threading
import hashlib
from Crypto import Random
import Crypto.Cipher.AES as AES
from Crypto.PublicKey import RSA
import signal
from lazyme.string import color_print
try: input = raw_input
except NameError: raw_input = input

def RemovePadding(s):
    print('RemovePadding:', s)
    return s.replace(b'`',b'')


def Padding(s):
    return s + ((16 - len(s) % 16) * '`')


def ReceiveMessage():
    while True:
        emsg = server.recv(1024)
        msg = RemovePadding(AESKey.decrypt(emsg))
        if msg == FLAG_QUIT:
            color_print("\n[!] Server was shutdown by admin", color="red", underline=True)
            os.kill(os.getpid(), signal.SIGKILL)
        else:
            color_print("\n[!] Server's encrypted message \n" + emsg, color="gray")
            print ("\n[!] SERVER SAID : ", msg)


def SendMessage():
    while True:
        msg = raw_input("[>] YOUR MESSAGE : ")
        en = AESKey.encrypt(Padding(msg))
        server.send(en)
        if msg == FLAG_QUIT:
            os.kill(os.getpid(), signal.SIGKILL)
        else:
            color_print("\n[!] Your encrypted message \n" + str(en), color="gray")


if __name__ == "__main__":
    #objects
    server = ""
    AESKey = ""
    FLAG_READY = "Ready"
    FLAG_QUIT = "quit"
    # 10.1.236.227
    # public key and private key
    random = Random.new().read
    RSAkey = RSA.generate(1024, random)
    #public = RSAkey.publickey().exportKey()
    #private = RSAkey.exportKey()




    if 0:
        host = raw_input("Host : ")
        port = int(input("Port : "))
    else:
        host = "127.0.0.1"
        port = 8080
    if 1:
        private = open('private.txt', 'rb').read()
        public = open('public.txt', 'rb').read()
        tmpPub = hashlib.md5(public)
        my_hash_public = tmpPub.hexdigest() 
        print (public)
        print ("\n",private)
    else:
        with open('private.txt', 'w'):
            pass
        with open('public.txt', 'w'):
            pass

        try:
            file = open('private.txt', 'wb')
            file.write(private)
            file.close()

            file = open('public.txt', 'wb')
            file.write(public)
            file.close()
        except BaseException:
            color_print("Key storing in failed", color="red", underline=True)
            raise

    check = False

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((host, port))
        check = True
    except BaseException:
        color_print("\n[!] Check Server Address or Port", color="red", underline=True)

    if check is True:
        color_print("\n[!] Connection Successful", color="green", bold=True)
        server.send(public + b":" + my_hash_public.encode())
        # receive server public key,hash of public,eight byte and hash of eight byte
        fGet = server.recv(1072*10)
        print(100,fGet)
        split = fGet.split(b":")
        toDecrypt = split[0]
        serverPublic = split[1]
        color_print("\n[!] Server's public key\n", color="blue")
        print (111, toDecrypt)
        #print (222, toDecrypt.decode('utf-8'))
        print(2222, private)
        decrypted = RSA.importKey(private).decrypt(toDecrypt)
        print(333, decrypted)
        splittedDecrypt = decrypted.split(b":")
        eightByte = splittedDecrypt[0]
        hashOfEight = splittedDecrypt[1]
        hashOfSPublic = splittedDecrypt[2]
        color_print("\n[!] Client's Eight byte key in hash\n", color="blue")
        print (hashOfEight)

        # hashing for checking
        sess = hashlib.md5(eightByte)
        session = sess.hexdigest()

        hashObj = hashlib.md5(serverPublic)
        server_public_hash = hashObj.hexdigest()
        color_print("\n[!] Matching server's public key & eight byte key\n", color="blue")
        print(456, server_public_hash, hashOfSPublic, server_public_hash == hashOfSPublic)
        print(456, session, hashOfEight, session == hashOfEight)
        if server_public_hash == hashOfSPublic.decode() and session == hashOfEight.decode():
            # encrypt back the eight byte key with the server public key and send it
            color_print("\n[!] Sending encrypted session key\n", color="blue")
            serverPublic = RSA.importKey(serverPublic).encrypt(eightByte, None)
            print(99999, serverPublic)
            server.send(serverPublic[0])
            # creating 128 bits key with 16 bytes
            color_print("\n[!] Creating AES key\n", color="blue")
            key_128 = eightByte + eightByte[::-1]
            AESKey = AES.new(key_128, AES.MODE_CBC,IV=key_128)
            # receiving ready
            serverMsg = server.recv(2048)
            serverMsg = RemovePadding(AESKey.decrypt(serverMsg))
            print('server ready :',serverMsg, FLAG_READY, serverMsg == FLAG_READY)
            if serverMsg.decode() == FLAG_READY:
                color_print("\n[!] Server is ready to communicate\n", color="blue")
                serverMsg = raw_input("\n[>] ENTER YOUR NAME : ")
                server.send(serverMsg.encode())
                threading_rec = threading.Thread(target=ReceiveMessage)
                threading_rec.start()
                threading_send = threading.Thread(target=SendMessage)
                threading_send.start()
            else:
                print(111, 'exiting...')
        else:
            color_print("\nServer (Public key && Public key hash) || (Session key && Hash of Session key) doesn't match", color="red", underline=True)
