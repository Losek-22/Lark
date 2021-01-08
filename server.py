from socket import socket, SOL_SOCKET, SO_REUSEADDR
from threading import Thread, Lock
import csv


def switchcase(receiveddata, c):
    """Serves as a communication between user clients and server, instead of if statements. First argument is a
    message sent by user client, second argument is the user's address."""

    switcher = {
        '*login attempt': checkcredentials,
        '*register': newuser,
        '*logout': useroffline,
        '*global message': globalmessage}
    func = switcher.get(receiveddata)
    return func(c)


def useroffline(c):
    """Deletes the user from online list"""

    with onlinelock:
        for key in list(onlineusers):
            if onlineusers[key] == c:
                print(f'User {key} logged out.')
                del onlineusers[key]
    return


def globalmessage(c):
    """Accepts a message sent on a global chat."""

    global onlineusers
    message = c.recv(4096).decode('utf8')
    with onlinelock:
        for user in onlineusers.keys():
            if onlineusers[user] == c:
                sender = user
                break
        for user in onlineusers.keys():
            onlineusers[user].sendall(sender.encode('utf8') + b"-" + message.encode('utf8'))
    return


def newuser(c):
    """Creates a new account using provided credentials. Takes the user's address as an argument"""

    global credentials
    global dblock
    c.sendall(b'r')  # ready?
    login = c.recv(4096).decode('utf8')
    password = c.recv(4096).decode('utf8')
    print(login)
    print(password)
    with dblock:
        if login not in credentials:
            with open('credentials.txt', mode='a', newline='') as passwords_csv:
                newuser_writer = csv.writer(passwords_csv)
                newuser_writer.writerow([login, password])
            updatecredentials()
            c.sendall(b'1')
            print(f'New user {login} registered from {c}')
        else:
            c.sendall(b'0')
    return


def checkcredentials(c):
    """Checks if given login and password are in the database, and if they match. Takes user's address as an argument"""

    global credentials
    global onlineusers
    global onlinelock
    global dblock
    c.sendall(b'r')  # ready?
    login = c.recv(4096).decode('utf8')
    password = c.recv(4096).decode('utf8')
    with dblock:
        if login in credentials.keys():
            if credentials[login] == password:
                c.sendall(b'1')
                with onlinelock:
                    onlineusers[login] = c
                print(f'User {login} logged in from {c}')
            else:
                c.sendall(b'0')
        else:
            c.sendall(b'0')
    return


def connection(c, a):
    """Establishes a new connection with an instance of Lark client. Takes socket.accept() as an argument."""

    print(f'New connection from {a}.')
    while True:
        try:
            x = c.recv(4096).decode('utf8')
            if x == '':
                c.close()
                print(f'Connection from {a} has ended.')
                useroffline(c)
                return
            else:
                switchcase(x, c)
        except:
            c.close()
            print(f'Connection from {a} has ended.')
            useroffline(c)
            return


def updatecredentials():
    with open('credentials.txt', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            credentials[row["login"]] = row["password"]
            line_count += 1
        print(f'Imported {line_count - 1} accounts.')  # -1 because of the headers


print('Server starting...')
s = socket()
s.bind(('localhost', 4444))
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.listen(1)

# reading account info from a .txt file
credentials = {}
updatecredentials()
onlineusers = {}
dblock = Lock()  # logins/passwords dictionary lock
onlinelock = Lock()  # online users dictionary lock

try:
    while True:
        w = Thread(target=connection, args=s.accept())
        w.daemon = True
        w.start()
finally:
    s.close()
