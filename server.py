from socket import socket, SOL_SOCKET, SO_REUSEADDR
from threading import Thread, Lock


def switchcase(receiveddata, c):
    """Serves as a communication between user clients and server, instead of if statements. First argument is a
    message sent by user client, second argument is the user's address."""
    switcher = {
        '*login attempt': checkcredentials,
        '*register': newuser,
        '*logout': useroffline,
        '*global message': globalmessage
    }
    func = switcher.get(receiveddata)
    return func(c)


def useroffline(c):
    """Deletes the user from online list"""
    with onlinelock:
        for key in list(onlineusers):
            if onlineusers[key] == c:
                del onlineusers[key]
    return


def globalmessage(c):
    """Accepts a message sent on a global chat."""
    global onlineusers
    global credentials
    print('przed przyjsicem')
    message = c.recv(4096).decode('utf8')
    print('po przyjsciu')
    with onlinelock:
        for user in onlineusers.keys():
            print(onlineusers[user])
            onlineusers[user].sendall(message.encode('utf8'))
    return


def newuser(c):
    """Creates a new account using provided credentials. Takes the user's address as an argument"""
    global credentials
    global dblock
    c.sendall(b'r')  # ready?
    login = c.recv(4096).decode('utf8')
    password = c.recv(4096).decode('utf8')
    with dblock:
        if login not in credentials:
            credentials[login] = password
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
        if login in credentials:
            if credentials[login] == password:
                c.sendall(b'1')
                with onlinelock:
                    onlineusers[login] = c
                print(f'User {login} logged in from {c}')
        else:
            c.sendall(b'0')
    return


def connection(c, a):
    """Establishes a new connection with an instance of Lark. Takes socket.accept() as an argument."""
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


s = socket()
s.bind(('localhost', 4444))
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.listen(1)
credentials = {}
credentials['losek'] = 'losek'  # for debugging
onlineusers = {}
dblock = Lock()  # accounts/password dictionary lock
onlinelock = Lock()  # online users dictionary lock

try:
    while True:
        w = Thread(target=connection, args=s.accept())
        w.daemon = True
        w.start()
finally:
    s.close()
