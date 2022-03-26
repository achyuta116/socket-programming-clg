# echo-client.py

import socket
import json
from datetime import datetime

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

def process_auth_response(res):
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
    elif (res_code == "MSET"):
        print('User Data:', res_supplement)
        

# need to implement
def process_data_response(res):
    pass

def send_to_server(send_message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        # s.sendall(bytes(send_message), 'utf-8')
        send_message = bytes(send_message,'utf-8')
        s.sendall(send_message)
        data = s.recv(1024)
        res = data.decode('utf-8')
        next_action = process_auth_response(res)
        print(f"Received {data!r}")
    return next_action


def user_menu(res, username):
    res_code, res_supplement = res.split(';')
    user_data = json.loads(res_supplement)
    while(True):
        print('--USER MENU--')
        #fill out usermenu
        #make the usermenu loop with socket connections as well
        #need to implement socket connection and send data to server properly
        #and handle data in the function on the server i.e process_data function in server.py
        print(user_data)
        print('1. Print Current Notifs')
        print('2. Print Set Notifs')
        print('3. Add a reminder')
        print('4. Set a meeting reminder')
        print('5. Clear Current Notifs')
        print('6. Exit')
        choice = int(input('Enter your choice: '))
        if(choice > 6 or choice < 1):
            print('Enter valid choice: ')
            continue
        else:
            if choice == 6: break
            data = ''
            # @Sourav, you might want to change the way you're looping through the reminders since Amogh implemented 
            # a different reminder format using dictionaries, you could refer choice 2 for this
            if choice == 1:
                if user_data['curr_notif'] == []:
                    print('No Current Notifications')
                for (time,detail) in user_data['curr_notif']:
                    print('Scheduled time:',time)
                    print('Details:',detail)
            elif choice == 2:
                if user_data['set_notif'] == []:
                    print('No Set Reminders')
                for reminder in user_data['set_notif']:
                    print("Reminder is set on: ", reminder['date'])
                    print('Reminder is set at: ', reminder['time'])
                    print('Reminder details: ', reminder['agenda'])
            elif choice == 3:
                date = input("Enter the date in YYYY-MM-DD format: ")
                time = input("Enter the time of reminder [24 hour format]: ")
                agenda = input("Enter the details of the reminder: ")
                message = "MEET^" + username + f"&{date} {time} {agenda}"
                send_to_server(message)
            elif choice == 4:
                print("Enter the invitees username")
                usernames = []
                while(True):
                    usn = input()
                    usernames.append(usn)
                    choice = input("Do you want to enter another username?(y/n)")
                    if(choice == 'n'):
                        break
                usernames.append(username)
                date = input("Enter the date in YYYY-MM-DD format: ")
                time = input("Enter the time of meeting [24 hour format]: ")
                agenda = input("Enter the agenda of the meeting: ")
                usernames = "MEET^" + ";".join(usernames) + f"&{date} {time} {agenda}"
                send_to_server(usernames)
            elif choice == 5:
                if user_data['curr_notif'] == []:
                    print('Successfully Reset Current Notifications')
                new_notif = []
                user_data['curr_notif'] = new_notif
                send_to_server(new_notif)

            continue

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
            next_action = process_auth_response(res)
            print(f"Received {data!r}") #recieve either user doc or incorrect auth
        if(next_action == 1):
            user_menu(res, username) #display usermenu make connection and use commands on server
        continue
    elif(choice == 3):
        print('Successfully Exited')
        break
    else: 
        print('Incorrect Choice')
        break
        