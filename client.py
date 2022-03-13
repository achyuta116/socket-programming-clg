# echo-client.py

import socket
import json

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

def process_response(res):
    res_code, res_supplement = res.split(';')
    if(res_code == 'REG'):
        print('User successfully registered.')
        return 1
    elif(res_code == 'EXS'):
        print('Username already exists signup with another username')
        return 0
    elif(res_code == 'EXI'):
        print('User logged in.')
        print('User Data:', res_supplement)
        return 1
    elif(res_code == 'INP'):
        print('Incorrect Password entered.')
        return 0
    elif(res_code == 'NEX'):
        print('User does not exist')
        return 0

def user_menu(res):
    res_code, res_supplement = res.split(';')
    user_data = json.loads(res_supplement)
    print('--USER MENU--')
    #fill out usermenu
    #make the usermenu loop with socket connections as well
    print(user_data)
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.connect((HOST, PORT))
    #     auth_supplement = bytes(username, 'utf-8')+bytes(';', 'utf-8')+bytes(password, 'utf-8')
    #     s.sendall((b'SIG^'if choice == 1 else b'LOG^') + auth_supplement)
    #     data = s.recv(1024)
    #     res = data.decode('utf-8')
    #     next_action = process_response(res)
    #     print(f"Received {data!r}")

while(True):
    print('--MENU--')
    print('1. Sign Up')
    print('2. Login')
    print('3. Exit')
    choice = int(input('Enter your choice: '))
    if(choice == 1 or choice == 2):
        username = input('Enter your username: ')
        password = input('Enter your password: ')
        next_action = 0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            auth_supplement = bytes(username, 'utf-8')+bytes(';', 'utf-8')+bytes(password, 'utf-8')
            s.sendall((b'SIG^'if choice == 1 else b'LOG^') + auth_supplement)
            data = s.recv(1024)
            res = data.decode('utf-8')
            next_action = process_response(res)
            print(f"Received {data!r}") #recieve either user doc or incorrect auth
        if(next_action == 1):
            user_menu(res) #display usermenu make connection and use commands on server
        continue
    elif(choice == 3):
        print('Successfully Exited')
        break
    else: 
        print('Incorrect Choice')
        break
        