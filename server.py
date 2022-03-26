import socket
import json
import threading
import multiprocessing

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
            data[username] = details
            with open('data.json', 'w') as outfile:
                    json.dump(data, outfile)
        elif(operation == "MEET"):
            usernames,datetime = supplement.split("&")
            usernames = usernames.split(";")
            date,time,agenda = datetime.split()
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
tot_process = []
def main():
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        # ip = socket.gethostbyname(socket.gethostname())
        print("Server Listening on:",HOST)
        while True:
            conn, addr = s.accept()
            process = multiprocessing.Process(target = handle_client,args = (conn,addr))
            process.start()
            # print(f"Currently Listening to {threading.active_count() - 1} connections")
if __name__ == "__main__":
    main()
