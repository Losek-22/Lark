from socket import socket
import tkinter as tk


class LogInWindow:
    """Log-in and register window."""

    def __init__(self, newlogin):

        # root window
        self.LogInWindow = newlogin
        self.LogInWindow.title('Lark')
        self.LogInWindow.resizable(False, False)
        self.LogInWindow.geometry(f'400x180+{int(self.LogInWindow.winfo_screenwidth() / 2) - 200}'  # centers window
                                  f'+{int(self.LogInWindow.winfo_screenheight() / 2) - 180}')

        # root background
        self.image = tk.PhotoImage(file="background.gif")
        self.panel = tk.Label(self.LogInWindow, image=self.image)
        self.panel.grid(row=0,
                        column=0,
                        rowspan=2,
                        columnspan=2)
        self.LogInWindow.bind('<Configure>', self.movebackground)

        # welcome message
        self.welcome = tk.Label(self.LogInWindow,
                                borderwidth=2,
                                relief='groove',
                                text='Welcome to Lark!'
                                     '\nEnter your login and password or register a new account.')
        self.welcome.grid(column=0,
                          row=0,
                          columnspan=2,
                          pady=(10, 10),
                          padx=(20, 20))

        # login entry
        self.loginLabel = tk.Label(self.LogInWindow,
                                   text='Your login:',
                                   borderwidth=2,
                                   relief='groove')
        self.loginLabel.grid(column=0,
                             row=1)
        self.loginEntry = tk.Entry(self.LogInWindow,
                                   width=15,
                                   justify='center')
        self.loginEntry.grid(row=2,
                             column=0,
                             pady=(10, 10))
        self.loginEntry.focus()

        # password entry
        self.passwordLabel = tk.Label(self.LogInWindow,
                                      text='Your password:',
                                      borderwidth=2,
                                      relief='groove')
        self.passwordLabel.grid(column=1,
                                row=1)
        self.passwordEntry = tk.Entry(self.LogInWindow,
                                      width=15,
                                      justify='center',
                                      show='*')
        self.passwordEntry.bind('<Return>', self.loginattempt)
        self.passwordEntry.grid(row=2,
                                column=1,
                                pady=(10, 10))

        # login button
        self.loginButton = tk.Button(self.LogInWindow,
                                     text='Log into Lark')
        self.loginButton.grid(row=3,
                              column=0)
        self.loginButton.bind('<Button-1>', self.loginattempt)

        # register button
        self.registerButton = tk.Button(self.LogInWindow,
                                        text='Register here')
        self.registerButton.grid(row=3,
                                 column=1)
        self.registerButton.bind('<Button-1>', self.registerwindow)

        # grid weight values
        self.LogInWindow.grid_columnconfigure(0, weight=1)
        self.LogInWindow.grid_columnconfigure(1, weight=1)

    def movebackground(self, event):
        """Moves the background image depending on the X and Y coordinates of the root window. The background seems
            to stay in place in relation to the moving root window."""

        self.panel.place(x=-1 * self.LogInWindow.winfo_x(), y=-1 * self.LogInWindow.winfo_y())

    def loginattempt(self, event):
        """Connects to the server and checks the credentials"""

        global s
        login = self.loginEntry.get().encode('utf8')
        password = self.passwordEntry.get().encode('utf8')
        if login and password:
            s.sendall(b'*login attempt')
            if s.recv(4096) == b'r':
                s.sendall(login)
                s.sendall(password)
                x = s.recv(4096)
                if x == b'0':  # login failed
                    self.passwordEntry.delete(0, tk.END)
                    self.loginEntry.delete(0, tk.END)
                    self.loginEntry.focus()
                    self.welcome.configure(text='The credentials you entered are incorrect.\nIf you do not '
                                           'have an account please register a new one.',
                                           background='yellow')
                else:  # login successful
                    self.LogInWindow.destroy()
                    mainwindow = tk.Tk()
                    root_main = MainChatWindow(mainwindow)
                    mainwindow.mainloop()
        return

    def registerwindow(self, event):
        """Changes the window to register window. Called by clicking the Register button in root window."""

        global s
        self.welcome.configure(text='You chose to create a new account.\nPlease enter your new login and password.',
                               background='#F0F0F0')
        self.loginLabel.configure(text='Your new login:')
        self.passwordLabel.configure(text='Your new password:')
        self.loginButton.configure(text='Return to the log-in window')
        self.loginButton.bind('<Button-1>', self.backtologin)
        self.registerButton.configure(text='Create your\nnew Lark account')
        self.registerButton.bind('<Button-1>', self.registerattempt)
        self.passwordEntry.delete(0, tk.END)
        self.loginEntry.delete(0, tk.END)
        self.loginEntry.focus()

    def registerattempt(self, event):
        """Attempts to create an account on the server."""

        login = self.loginEntry.get().encode('utf8')
        password = self.passwordEntry.get().encode('utf8')
        s.sendall(b'*register')
        if s.recv(4096) == b'r':
            if login and password:
                s.sendall(login)
                s.sendall(password)
                x = s.recv(4096)
                if x == b'0':  # register failed
                    self.welcome.configure(text='The login you chose is taken.\nYou need to choose another one.',
                                           background='yellow')
                else:  # register successful
                    self.welcome.configure(text='Your account has been successfully created.\n'
                                                'You can now go back and log in.',
                                           background='green')
                    self.loginButton.configure(background='green')
        self.passwordEntry.delete(0, tk.END)
        self.loginEntry.delete(0, tk.END)
        return

    def backtologin(self, event):
        """Returns to the login window from register window."""

        self.welcome.configure(text='Welcome to the Lark '
                                    'communicator!\nEnter your login and password or register a new account.',
                               background='#F0F0F0')
        self.loginLabel.configure(text='Your login:')
        self.passwordLabel.configure(text='Your password:')
        self.loginButton.configure(text='Log into Lark')
        self.loginButton.bind('<Button-1>', self.loginattempt)
        self.registerButton.configure(text='Register here')
        self.registerButton.bind('<Button-1>', self.registerwindow)
        self.loginButton.configure(background='#F0F0F0')
        self.loginEntry.focus()
        self.passwordEntry.delete(0, tk.END)
        self.loginEntry.delete(0, tk.END)
        return


class MainChatWindow:
    """Window responsible for global chat."""

    def __init__(self, main):

        self.message = ''

        # root window
        self.mainwindow = main
        self.mainwindow.title('Lark')
        self.mainwindow.geometry(f'800x600+{int(self.mainwindow.winfo_screenwidth() / 2) - 400}'  # centers window
                                 f'+{int(self.mainwindow.winfo_screenheight() / 2) - 400}')
        self.mainwindow.configure(background='black')
        self.mainwindow.minsize(800, 600)

        # menu
        self.menubar = tk.Menu(self.mainwindow)
        self.menubar.add_command(label='Log out',
                                 command=self.logout)
        self.menubar.add_command(label='Exit',
                                 command=lambda: exit())
        self.thememenu = tk.Menu(self.mainwindow,
                                 tearoff=False)
        self.thememenu.add_command(label='Light theme',
                                   command=self.lighttheme)
        self.thememenu.add_command(label='Dark theme',
                                   command=self.darktheme)
        self.menubar.add_cascade(label='Set theme...',
                                 menu=self.thememenu)
        self.mainwindow.config(menu=self.menubar)

        # chatbox
        self.chatbox = tk.Text(self.mainwindow,
                               wrap='word')
        self.chatbox.grid(row=0,
                          column=0,
                          columnspan=2,
                          sticky='W'+'E'+'N'+'S')
        self.chatbox.insert(1.0, 'Welcome to general chat room. You can now post your message by typing it into '
                                 'the space below.')

        # message input label
        self.yourmessageLabel = tk.Label(self.mainwindow,
                                         text='You:',
                                         background='black',
                                         fg='white')
        self.yourmessageLabel.grid(row=1,
                                   column=0)

        # message input
        self.messageEntry = tk.Entry(self.mainwindow,
                                     fg='gray')
        self.messageEntry.insert(0, 'Enter your message here...')
        self.messageEntry.bind('<Button-1>', self.entermessage)
        self.messageEntry.bind('<Return>', self.sendmessage)
        self.messageEntry.grid(row=1,
                               column=1,
                               sticky='E'+'W',
                               pady=(5, 5),
                               padx=(5, 5))

        # send button
        self.sendButton = tk.Button(self.mainwindow,
                                    text='Send')
        self.sendButton.grid(row=1,
                             column=2,
                             padx=(5, 5),
                             pady=(5, 5),
                             sticky='E'+'W')
        self.sendButton.bind('<Button-1>', self.sendmessage)

        # grid weight values
        self.mainwindow.grid_columnconfigure(1, weight=1)
        self.mainwindow.grid_rowconfigure(0, weight=1)

        self.wasgraytextdeleted = 1  # a variable used in sendmessage function

        self.mainwindow.after(100, self.receivemessage()) # if it's not commented, the window fails to show

    def receivemessage(self):
        self.message = s.recv(4096).decode('utf8')
        print(self.message)  # TUTAJ JEST BŁĄD, NIE PRINTUJE NIC
        self.chatbox.insert(tk.END, self.message)  # work in progress, just trying to make it work for now

    def entermessage(self, event):
        """Deletes the 'enter your message here...' on click on the Entry box"""
        if self.wasgraytextdeleted:
            self.messageEntry.configure(fg='black')
            self.messageEntry.delete(0, tk.END)
            self.wasgraytextdeleted = 0
        return

    def sendmessage(self, event):
        global s
        if self.messageEntry.get():
            s.sendall(b'*global message')
            s.sendall(self.messageEntry.get().encode('utf8'))
            self.messageEntry.delete(0, tk.END)
        return

    def logout(self):
        """Promts the server to log the user out, then opens login window again."""

        global isloggedin
        isloggedin = 0
        self.mainwindow.destroy()
        s.sendall(b'*logout')
        newlogin = tk.Tk()
        root = LogInWindow(newlogin)
        newlogin.mainloop()

    def darktheme(self):
        """Changes chatbox window theme to dark."""

        self.chatbox.configure(background='black',
                               fg='white')

    def lighttheme(self):
        """Changes chatbox window theme to dark."""

        self.chatbox.configure(background='white',
                               fg='black')


s = socket()
s.connect(('localhost', 4444))
newLogin = tk.Tk()
root = LogInWindow(newLogin)
newLogin.mainloop()
