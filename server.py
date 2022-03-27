import socket
import json
import threading
import multiprocessing
from datetime import datetime
import time

def process_data(command):
    res = ''
    with open('data.json') as json_file:
        data = json.load(json_file)
        (operation, supplement) = command.split('^')
        if(operation == 'LOG'):
            (username, password) = supplement.split(';')
            if(username in data and data[username]['password'] == password):
                res = 'EXI;' + json.dumps(data[username])
            elif(username in data):
                res = 'INP;'
            else: res = 'NEX;'
        elif(operation == 'SIG'):
            (username, password) = supplement.split(';')
            if(username not in data):
                data[username] = {
                    'password':password,
                    'set_notif':[], 
                    'curr_notif':[]
                }
                with open('data.json', 'w') as outfile:
                    json.dump(data, outfile)
                res = 'REG;' + json.dumps(data[username])
            else: res = 'EXS;'
        elif(operation == 'UPD'):
            (username, details) = supplement.split('|')
            res = "MSET;"
            if username in data:
                data[username]['curr_notif'] = []
                res += json.dumps(data[username])
            # data[username['curr_notif']] = details    
            with open('data.json', 'w') as outfile:
                    json.dump(data, outfile)

        elif(operation == "MEET"):
            usernames,datetime = supplement.split("&")
            usernames = usernames.split(";")
            date,time,agenda = datetime.split('$')
            res = "MSET;"
            for usn in usernames:
                if usn in data:
                    meet = {}
                    meet["date"] = date
                    meet["time"] = time
                    meet["agenda"] = agenda
                    data[usn]["set_notif"].append(meet)
                    res += json.dumps(data[usn])
            with open('data.json', 'w') as outfile:
                json.dump(data, outfile)
        elif(operation == "CNOT"):
            usn = supplement
            res = "CNOTP&"
            cur_notif = data[usn]["curr_notif"]
            i = 0
            length = len(cur_notif)
            while i < length:
                res += f"{cur_notif[i]};"
                data[usn]["curr_notif"].pop(i)
                length -= 1
            # for i in range(len(cur_notif)):
            #     res += f"{cur_notif[i]};"
            #     data[usn]["curr_notif"].pop(i)
            with open('data.json', 'w') as outfile:
                json.dump(data, outfile)

    return res

def handle_client(conn,addr):
    format = "utf-8"
    size = 1024
    print(f"[NEW CONNECTION] {addr}")
    with conn:
        while True:
            data = conn.recv(size)
            if not data:
                break
            response = process_data(data.decode(format))
            conn.sendall(bytes(response, format))
    conn.close()
    return

def update_data(name):
    while True:
        now = datetime.now()
        now_date = now.strftime("%Y-%m-%d")
        now_time = now.strftime("%H:%M")
        # print(f"now: {date} {time}")
        with open('data.json') as json_file:
            data = json.load(json_file)
            # print(type(data))
            for usn in data:
                # print(type(usn),usn)
                set_notif = data[usn]["set_notif"]
                for index in range(len(set_notif)):
                    notif = set_notif[index]
                    # print(notif["date"]<=now_date)
                    # print(notif["time"]<=now_time)
                    if notif["date"] <= now_date:
                        if notif["time"] <= now_time:
                            data[usn]["curr_notif"].append(notif)
                            data[usn]["set_notif"].pop(index)
                            # print("current:",data[usn]["curr_notif"])
                            # print("set:",data[usn]["set_notif"])
                            # print("updated")
                            with open('data.json', 'w') as outfile:
                                json.dump(data, outfile)
                                # print(f"data:{data}")       
            
        time.sleep(1)       

tot_process = []

def main():
    HOST = "127.0.0.1"
    PORT = 65432
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        # ip = socket.gethostbyname(socket.gethostname())
        print("Server Listening on:",HOST)
        while True:
            data_updation = threading.Thread(target=update_data, args=(1,))
            data_updation.start()
            conn, addr = s.accept()
            process = multiprocessing.Process(target = handle_client,args = (conn,addr))
            process.start()
            
            print(f"Currently Listening to {threading.active_count() - 1} connections")
if __name__ == "__main__":
    main()
