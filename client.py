import socket
import json
from datetime import datetime
import threading
import time

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
LOGIN = 0
EXIT = 0

class User_data:
    __shared_state = dict()

    def __init__(self):
        self.__dict__ = self.__shared_state
        self.state = {}

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
        return 1
    elif(res_code == 'INP'):
        print('Incorrect Password entered.')
        return 0
    elif(res_code == 'NEX'):
        print('User does not exist')
        return 0
    elif (res_code == "MSET"):
        print('Meeting set successfully')
    elif (res_code == 'CUR'):
        pass
        

# need to implement
def process_data_response(res):
    pass

def send_to_server(send_message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        send_message = bytes(send_message,'utf-8')
        s.sendall(send_message)
        data = s.recv(1024)
        res = data.decode('utf-8')
        next_action = process_auth_response(res)
    return next_action

def check_notifs(user_data, username):

    while True:
        data = user_data.state
        
        if user_data.state["curr_notif"]:
            index = 0
            length = len(user_data.state["curr_notif"])
            while index < length:
                notif = data["curr_notif"][index]
                print("Reminder is set on: ", notif['date'])
                print('Reminder is set at: ', notif['time'])
                print('Reminder details: ', notif['agenda'])
                user_data.state["curr_notif"].pop(index)
                index+=1
                length-=1
        else:
            for usn in data:
                # print(type(usn),usn)
                now = datetime.now()
                now_date = now.strftime("%Y-%m-%d")
                now_time = now.strftime("%H:%M")
                set_notif = user_data.state["set_notif"]
                index = 0
                length = len(user_data.state["set_notif"])
                while index < length:
                    notif = user_data.state["set_notif"][index]
                    if notif["date"] <= now_date:
                        if notif["time"] <= now_time:
                            user_data.state["curr_notif"].append(notif)
                            user_data.state["set_notif"].pop(index)
                    index+=1
                    length-=1   
        send_to_server("UPD^" + username + f"|")
        time.sleep(1)


def user_menu(res, username):
    res_code, res_supplement = res.split(';')
    user_data = User_data()
    copy = User_data()
    user_data.state = json.loads(res_supplement)
    print(user_data.state)
    check_for_notifs = threading.Thread(target=check_notifs, args=(copy,username))
    check_for_notifs.start()
    while(True):
        print('--USER MENU--')
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
            if choice == 6: 
                LOGIN = 0
                break
            if choice == 1:
                if user_data.state['curr_notif'] == []:
                    print('--No Current Notifications')
                else:
                    cur_notif = user_data.state['curr_notif']
                    print(f"The total Notifications currently set are {len(cur_notif)}")
                    print(f"Detailed Notifications:")
                    i = 1;
                    for notif in cur_notif:
                        print(f"{i}.)")
                        temp1 = notif['date']
                        temp2 = notif['time']
                        temp3 = notif['agenda']
                        print(f"--Scheduled date: {temp1}")
                        print(f"--Scheduled time:{temp2}")
                        print(f"--Details of the remainder:{temp3}")
                        i = i + 1
            elif choice == 2:
                if user_data.state['set_notif'] == []:
                    print('No Set Reminders')
                for reminder in user_data.state['set_notif']:
                    print("Reminder is set on: ", reminder['date'])
                    print('Reminder is set at: ', reminder['time'])
                    print('Reminder details: ', reminder['agenda'])
            elif choice == 3:
                date = input("Enter the date in YYYY-MM-DD format: ")
                time = input("Enter the time of reminder [24 hour format]: ")
                agenda = input("Enter the details of the reminder: ")
                user_data.state['set_notif'].append({
                    'date': date,
                    'time': time,
                    'agenda': agenda
                })
                message = "MEET^" + username + f"&{date}${time}${agenda}"
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
                usernames = "MEET^" + ";".join(usernames) + f"&{date}${time}${agenda}"
                send_to_server(usernames)
            elif choice == 5:
                if user_data.state['curr_notif'] == []:
                    print('Successfully Reset Current Notifications')
                message = "UPD^" + username + f"|"
                user_data.state['curr_notif'] = []
                send_to_server(message)

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
        if(next_action == 1):
            user_menu(res, username)
        continue
    elif(choice == 3):
        EXIT = 1
        print('Successfully Exited')
        break
    else: 
        print('Incorrect Choice')
        break
        