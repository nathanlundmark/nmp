import key_sync, nmp, time
import sys, os
import threading

global running
running = True

waittime = 60*2

def handler():
    while running:
        while running:
            t = time.time()
            try:
                if nmp.fetch() == False:
                    break
            except:
                while time.time() < t+60 and running:
                    time.sleep(1)
        
        while time.time() < t+waittime and running:
            time.sleep(1)


key_sync.set_org((sys.argv[2], 12300))

if sys.argv[3] == "genkeys":
    key_sync.new_rsa_keys()
    print("Done!")

elif sys.argv[3] == "init":
    try:
        nmp.init()
    except:
        print("You are on pause")

elif sys.argv[3] == "keychange":
    try:
        nmp.keychange()
    except:
        print("You are on pause")





elif sys.argv[3] == "ping":
    try:
        user = sys.argv[4]
        data = {
            "title": "ping",
            "type": "text",
            "text": "ping"
        }
        nmp.send(user, data)
    except:
        print("You are on pause")

elif sys.argv[3] == "spamping":
    while True:
        try:
            user = sys.argv[4]
            data = {
                "title": "ping",
                "type": "text",
                "text": "ping"
            }
            nmp.send(user, data)
        except:
            time.sleep(10)





elif sys.argv[3] == "sendmsg":
    try:
        nmp.sendmsg()
    except:
        print("You are on pause")

elif sys.argv[3] == "sendmsg-line":
    try:
        user = sys.argv[4]
        title = sys.argv[5]
        msg = sys.argv[6]
        data = {
            "title": title,
            "type": "text",
            "text": msg
        }
        nmp.send(user, data)
    except:
        print("You are on pause")

elif sys.argv[3] == "sendmail":
    try:
        user = input("To: ")
        title = input("Title: ")
        os.system("nano ./_nmp_client_msg_cache.txc")
        with open("./_nmp_client_msg_cache.txc", "r") as f:
            msg = f.read()
        os.remove("./_nmp_client_msg_cache.txc")

        data = {
            "title": title,
            "type": "text",
            "text": msg
        }
        nmp.send(user, data)
    except:
        print("You are on pause")

elif sys.argv[3] == "sendfile":
    nmp.send_file(sys.argv[4])






elif sys.argv[3] == "fetch":
    try:
        nmp.fetch()
    except:
        print("You are on pause, try using `fatchall`")

elif sys.argv[3] == "fetchall":
    while True:
        try:
            if nmp.fetch() == False:
                break
        except:
            time.sleep(10)

elif sys.argv[3] == "open":
    nmp.open_file(sys.argv[4])

elif sys.argv[3] == "cli":
    started = False
    worker = threading.Thread(target=handler, args=())
    while running:
        prompt = input("")
        if prompt == "start" and started == False:
            worker.start()
            started = True

        elif prompt == "exit":
            running = False

        elif prompt == "fetch":
            try:
                nmp.fetch()
            except:
                print("You are on pause")

        elif prompt == "fetchall":
            while True:
                try:
                    if nmp.fetch() == False:
                        break
                except:
                    print("You are on pause")
                    break

        elif prompt == "sendmsg":
            try:
                nmp.sendmsg()
            except:
                print("You are on pause")


        elif prompt == "sam":
            nmp.save_messages = not nmp.save_messages
            print(nmp.save_messages)

        elif prompt == "sdm":
            m = input("Please select a mode (s,p,d,o) ")
            modes = {
                "s": "save",
                "p": "preview",
                "d": "ignore",
                "o": "prompt"
            }
            if m in set("spdo"):
                nmp.prompt_downloads = m
                print("Set to mode: " + modes[m])
            else:
                print("Failed!")

        elif prompt == "open":
            nmp.open_file(input("File: "))

        elif prompt == "time":
            waittime = int(input("New time? "))