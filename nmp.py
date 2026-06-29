import rsa, base64, struct, json, socket, hashlib, time
import os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import key_sync

prompt_downloads = "Prompt"
def change_prompt_downloads(s):
    global prompt_downloads
    prompt_downloads = s

def get_buffer(conn):
    # Read exactly 4 bytes
    length = struct.unpack("!I", conn.recv(4))[0]
    # Read exactly 'length' bytes
    buf = b""
    while len(buf) < length:
        buf += conn.recv(length - len(buf))

    return buf


# Interface

def validate(conn):
    data = json.dumps({"user": sys.argv[1]}).encode("utf-8")
    conn.sendall(struct.pack("!I", len(data)))
    conn.sendall(data)

    buf = get_buffer(conn)

    try:
        _, priv = key_sync.get_rsa_keys()
        k = rsa.decrypt(buf, priv)
        hash = hashlib.sha256(k).digest()

        conn.sendall(hash)
    except:
        return


def send_nmp_mail(mail, to, adr):
    try:
        sock = socket.create_connection(adr)
    except:
        print("Send failed! Connection refused!")
        return False

    validate(sock)

    mail["version"] = 1
    mail["type"] = "send"
    mail["to"] = to
    data = json.dumps(mail).encode("utf-8")

    sock.sendall(struct.pack("!I", len(data)))
    sock.sendall(data)

    sock.close()

    return True


def users_pub_key(user):
    try:
        sock = socket.create_connection(key_sync.get_org())
    except:
        print("Send failed! Connection refused!")
        return False

    validate(sock)

    p = {
        "type": "userlookup",
        "version": 1,
        "user": user
    }
    data = json.dumps(p).encode("utf-8")

    sock.sendall(struct.pack("!I", len(data)))
    sock.sendall(data)

    buf = get_buffer(sock)
    sock.close()

    obj = json.loads(buf.decode("utf-8"))
    key = rsa.PublicKey.load_pkcs1(obj["key"].encode("ascii"))

    return key






# Open an email
def nmp_open(mail):
    _, priv = key_sync.get_rsa_keys()
    hex_key = rsa.decrypt(
        base64.b64decode(
            mail["key"].encode("ascii")
        ),
    priv)
    key = bytes.fromhex(hex_key.decode("utf-8"))
    aes = AESGCM(key)
    blob = base64.b64decode(
            mail["blob"].encode("ascii")
        )
    nonce = blob[:12]
    ciphertext = blob[12:]
    data = aes.decrypt(nonce, ciphertext, None)
    obj = json.loads(data.decode("utf-8"))

    from_user = mail.get("from")
    if from_user != None:
        print("Mail from: `" + from_user + "`")
    else:
        print("Mail from: <Unknown> (Caution, unknown users could be anyone!)")

    if obj["type"] == "text":
        print("Title: " + obj["title"] + "\n" + obj["text"])
    elif obj["type"] == "file":
        file = base64.b64decode(
            obj["text"].encode("ascii")
        )
        while True:
            if prompt_downloads == "Prompt":
                prompt = input("This email `" + obj["title"] + "` contains a file. Would you like to preview, save, or ignore (p,s,d)?")
            else:
                prompt = prompt_downloads
            if prompt == "p":
                print(file)
            elif prompt == "d":
                break
            elif prompt == "s":
                fn = ""

                if prompt_downloads != "s":
                    fn = input("Please enter a filemame to save as (Leave blank to save as email name): ")

                if fn == "":
                    fn = str(time.time()) + ".nmpadf"

                with open(fn, "wb") as f:
                    f.write(file)

                print("Saved `" + obj["title"] + "` as `" + fn + "`")
                break
        
            if prompt_downloads != "Prompt":
                break
    else:
        print(obj)





def encrypt(data, pub_key):
    key = AESGCM.generate_key(bit_length=256)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    blob = nonce + aes.encrypt(nonce, json.dumps(data).encode("utf-8"), None)

    return blob, rsa.encrypt(key.hex().encode("utf-8"), pub_key)

def send(user, data):
    pub_key = users_pub_key(user)

    blob, key = encrypt(data, pub_key)
    mail = {
        "key": base64.b64encode(key).decode("ascii"),
        "blob": base64.b64encode(blob).decode("ascii")
    }

    send_nmp_mail(mail, user, key_sync.get_org())



# Send


def sendmsg():
    user = input("To: ")
    title = input("Title: ")
    msg = input("Message: ")
    data = {
        "title": title,
        "type": "text",
        "text": msg
    }
    send(user, data)

def send_file(fn):
    user = input("To: ")
    title = input("Title (leave empty to use file name): ")
    if title == "":
        title = fn

    with open(fn, "rb") as f:
        msg = f.read()

    data = {
        "title": title,
        "type": "file",
        "text": base64.b64encode(msg).decode("ascii")
    }
    send(user, data)


#get

def fetch():
    try:
        sock = socket.create_connection(key_sync.get_org())
    except:
        print("Send failed! Connection refused!")
        return False

    validate(sock)

    data = json.dumps({"type": "get", "version": 1, "to": sys.argv[1]}).encode("utf-8")

    sock.sendall(struct.pack("!I", len(data)))
    sock.sendall(data)



    # Read exactly 4 bytes
    length = struct.unpack("!I", sock.recv(4))[0]
    # Read exactly 'length' bytes
    buf = b""
    while len(buf) < length:
        buf += sock.recv(length - len(buf))

    sock.close()

    #try:
    obj = json.loads(buf.decode("utf-8"))
    if obj["type"] == "empty":
        return False

    nmp_open(obj)
    return True





# Misc

def init():
    try:
        sock = socket.create_connection(key_sync.get_org())

    except:
        print("Send failed! Connection refused!")
        return False

    pub, _ = key_sync.get_rsa_keys()

    mail = {
        "version": 1,
        "type": "init",
        "user": sys.argv[1],
        "key": pub.save_pkcs1().decode("ascii")
    }
    data = json.dumps(mail).encode("utf-8")

    sock.sendall(struct.pack("!I", len(data)))
    sock.sendall(data)

    sock.close()

def keychange():
    try:
        sock = socket.create_connection(key_sync.get_org())

    except:
        print("Send failed! Connection refused!")
        return False

    validate(sock)

    key_sync.new_rsa_keys()
    pub, _ = key_sync.get_rsa_keys()

    mail = {
        "version": 1,
        "type": "keychange",
        "key": pub.save_pkcs1().decode("ascii")
    }
    data = json.dumps(mail).encode("utf-8")

    sock.sendall(struct.pack("!I", len(data)))
    sock.sendall(data)

    sock.close()

