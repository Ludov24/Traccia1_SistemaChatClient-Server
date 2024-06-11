#!/usr/bin/env python3

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tkt
from tkinter import messagebox

def receive():
    """
    Funzione per ricevere i messaggi dal server in modo continuo.
    """
    while connected:
        try:
            # Riceve messaggi dal server
            msg = clientSocket.recv(BUFSIZ).decode("utf8")
            if msg.startswith("/userlist"):
                # Aggiorna la lista degli utenti online
                user_list = msg.split(" ", 1)[1].split(",")
                onlineUsersList.delete(0, tkt.END)
                for user in user_list:
                    onlineUsersList.insert(tkt.END, user)
            elif msg:
                msgList.insert(tkt.END, msg)
        except OSError as e:
            # Stampa l'errore se c'è un problema nella ricezione dei messaggi
            if connected:  # Mostra l'errore solo se il client è ancora connesso
                print(f"Errore nel ricevere messaggi: {e}")
            break

def send(event=None):
    """
    Funzione per inviare i messaggi al server.
    """
    msg = myMsg.get()
    myMsg.set("")  # Pulisce il campo di input dopo aver preso il messaggio
    try:
        # Invia il messaggio al server
        clientSocket.send(bytes(msg, "utf8"))
    except OSError as e:
        # Se c'è un errore, mostra il messaggio di errore nella Listbox
        msgList.insert(tkt.END, f"Errore di connessione. Impossibile inviare il messaggio: {e}")

def onDisconnect():
    """
    Funzione per disconnettersi dal server senza chiudere la finestra.
    """
    global connected
    connected = False  # Aggiorna lo stato di connessione
    try:
        # Invia il comando di disconnessione al server
        clientSocket.send(bytes("/quit", "utf8"))
        clientSocket.close()
        # Disabilita i campi di input e i pulsanti
        entryField.config(state=tkt.DISABLED)
        sendButton.config(state=tkt.DISABLED)
        disconnectButton.config(state=tkt.DISABLED)
        # Mostra il messaggio di disconnessione nella Listbox
        msgList.insert(tkt.END, "Sei stato disconnesso.")
    except OSError as e:
        # Se c'è un errore, mostra il messaggio di errore nella Listbox
        msgList.insert(tkt.END, f"Errore nella disconnessione: {e}")

def onClosing(event=None):
    """
    Funzione chiamata quando la finestra viene chiusa.
    """
    onDisconnect()
    mainWindow.quit()

def login(event=None):
    """
    Funzione per gestire il login dell'utente.
    """
    name = nameVar.get()
    if name:
        try:
            # Invia il nome utente al server
            clientSocket.send(bytes(name, "utf8"))
            # Disabilita i campi di input del nome e del pulsante di login
            entryName.config(state=tkt.DISABLED)
            loginButton.config(state=tkt.DISABLED)
            # Abilita i campi di input dei messaggi e del pulsante di invio
            entryField.config(state=tkt.NORMAL)
            sendButton.config(state=tkt.NORMAL)
            disconnectButton.config(state=tkt.NORMAL)
        except OSError as e:
            # Mostra un messaggio di errore se c'è un problema di connessione
            messagebox.showerror("Errore", f"Errore di connessione: {e}")
    else:
        # Mostra un messaggio di avviso se il nome utente è vuoto
        messagebox.showwarning("Attenzione", "Il nome utente non può essere vuoto.")

def onEntryClick(event):
    """
    Funzione per rimuovere il placeholder quando l'utente clicca sull'entry.
    """
    if myMsg.get() == "Scrivi qui i tuoi messaggi.":
        myMsg.set("")
        entryField.config(fg='black')

def onFocusout(event):
    """
    Funzione per reimpostare il placeholder quando l'entry perde il focus e il campo è vuoto.
    """
    if myMsg.get() == "":
        myMsg.set("Scrivi qui i tuoi messaggi.")
        entryField.config(fg='grey')

# Creazione della finestra principale dell'applicazione
mainWindow = tkt.Tk()
mainWindow.title("MultiChatPy")

# Variabile per memorizzare il nome utente
nameVar = tkt.StringVar()

# Creazione del frame per il login
loginFrame = tkt.Frame(mainWindow)
tkt.Label(loginFrame, text="Inserisci il tuo nome:").pack(side=tkt.LEFT)
entryName = tkt.Entry(loginFrame, textvariable=nameVar)
entryName.pack(side=tkt.LEFT)
entryName.bind("<Return>", login)  # Aggiunge il binding del tasto Invio per il login
loginButton = tkt.Button(loginFrame, text="Login", command=login)
loginButton.pack(side=tkt.LEFT)
loginFrame.pack()

# Creazione del frame per visualizzare i messaggi della chat
messagesFrame = tkt.Frame(mainWindow)
myMsg = tkt.StringVar()
myMsg.set("Scrivi qui i tuoi messaggi.")
scrollbar = tkt.Scrollbar(messagesFrame)

# Creazione della Listbox per visualizzare i messaggi
msgList = tkt.Listbox(messagesFrame, height=15, width=60, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkt.RIGHT, fill=tkt.Y)
msgList.pack(side=tkt.LEFT, fill=tkt.BOTH)
msgList.pack()
messagesFrame.pack()

# Creazione della Listbox per visualizzare gli utenti online
onlineUsersFrame = tkt.Frame(mainWindow)
onlineUsersLabel = tkt.Label(onlineUsersFrame, text="User online:")
onlineUsersLabel.pack()
onlineUsersList = tkt.Listbox(onlineUsersFrame, height=10, width=30)
onlineUsersList.pack()
onlineUsersFrame.pack(side=tkt.RIGHT, padx=10)

# Creazione del campo di input per i messaggi
entryField = tkt.Entry(mainWindow, textvariable=myMsg, state=tkt.DISABLED, fg='grey')
entryField.bind("<Return>", send)
entryField.bind("<FocusIn>", onEntryClick)
entryField.bind("<FocusOut>", onFocusout)
entryField.pack()
sendButton = tkt.Button(mainWindow, text="Send", command=send, state=tkt.DISABLED)
sendButton.pack()

# Creazione del pulsante di disconnessione
disconnectButton = tkt.Button(mainWindow, text="Logout", command=onDisconnect, state=tkt.DISABLED)
disconnectButton.pack()

# Configurazione della funzione di chiusura della finestra
mainWindow.protocol("WM_DELETE_WINDOW", onClosing)

# Configurazione del server
HOST = input('Inserire il Server host (default: localhost): ')
if not HOST:
    HOST = 'localhost'
PORT = input('Inserire la porta del server host (default: 1606): ')
if not PORT:
    PORT = 1606
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

# Creazione del socket per la connessione al server
clientSocket = socket(AF_INET, SOCK_STREAM)

try:
    # Tentativo di connessione al server
    clientSocket.connect(ADDR)
except OSError as e:
    # Stampa un messaggio di errore e termina l'applicazione se non riesce a connettersi
    print(f"Errore di connessione: {e}")
    exit(1)

# Variabile di stato per la connessione
connected = True

# Avvio del thread per ricevere i messaggi dal server
receiveThread = Thread(target=receive)
receiveThread.start()
# Avvio del loop principale di Tkinter per la GUI
tkt.mainloop()
