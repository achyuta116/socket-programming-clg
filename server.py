import socket
import json

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

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
    return res




with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                #process data recieved
                if not data:
                    break
                response = process_data(data.decode('utf-8'))
                conn.sendall(bytes(response, 'utf-8'))