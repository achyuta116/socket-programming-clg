# echo-client.py

import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
while(True):
    print('--MENU--')
    print('1. Sign Up')
    print('2. Login')
    print('3. Exit')
    choice = int(input('Enter your choice: '))
    if(choice == 1 or choice == 2):
        username = input('Enter your username: ')
        password = input('Enter your password: ')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            auth_supplement = bytes(username, 'utf-8')+bytes(';', 'utf-8')+bytes(password, 'utf-8')
            s.sendall((b'SIG^'if choice == 1 else b'LOG^') + auth_supplement)
            data = s.recv(1024)

            print(f"Received {data!r}") #recieve either user doc or incorrect auth
        break
    elif(choice == 3):
        print('Successfully Exited')
        break
    else: 
        print('Incorrect Choice')
        break
        