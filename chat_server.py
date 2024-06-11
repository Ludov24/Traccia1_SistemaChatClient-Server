#!/usr/bin/env python3

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

def manageIncomingConnections():
    """
    Funzione per accettare le connessioni in entrata.
    Rimane in ascolto per nuove connessioni e crea un nuovo thread per ciascun client che si connette.
    """
    while True:
        try:
            # Accetta una nuova connessione
            client, clientAddress = server.accept()
            print(f"{clientAddress[0]}:{clientAddress[1]} si è collegato.")
            # Invia un messaggio di benvenuto al nuovo client
            client.send(bytes("Benvenuto/a! Inserisci il tuo nome.", "utf8"))
            # Salva l'indirizzo del client nel dizionario 'ipAddress'
            ipAddress[client] = clientAddress
            # Crea e avvia un nuovo thread per gestire la connessione del client
            Thread(target=manageClient, args=(client,)).start()
        except OSError as e:
            # Gestisce l'errore se c'è un problema nell'accettare le connessioni
            print(f"Errore nell'accettare connessioni: {e}")
            break

def manageClient(client):
    """
    Funzione per gestire un singolo client.
    Riceve il nome del client, gestisce i messaggi inviati dal client e si occupa della disconnessione del client.
    """
    try:
        # Riceve il nome del client
        name = client.recv(BUFSIZ).decode("utf8")
        # Crea e invia un messaggio di benvenuto personalizzato al client
        msgWelcome = f'{name} ti sei loggato correttamente,\nper abbandonare la Chat clicca su "Disconnetti".'
        client.send(bytes(msgWelcome, "utf8"))
        # Notifica a tutti i client che un nuovo utente si è unito alla chat
        msg = f"{name} si è unito alla chat!"
        broadcast(bytes(msg, "utf8"))
        # Aggiunge il client e il suo nome al dizionario 'clients'
        clients[client] = name

        # Aggiorna la lista degli utenti
        update_user_list()

        while True:
            # Riceve i messaggi dal client
            msg = client.recv(BUFSIZ)
            if not msg:
                break  # Se non ci sono messaggi, interrompe il ciclo
            if msg.decode("utf8") == "/quit":
                # Se il messaggio è '/quit', disconnette il client
                client.send(bytes("Sei stato disconnesso.", "utf8"))
                client.close()
                del clients[client]
                broadcast(bytes(f"{name} ha lasciato la chat.", "utf8"))
                print(f"L'utente {name} si è disconnesso volontariamente.")
                update_user_list()  # Aggiorna la lista degli utenti
                break
            else:
                # Altrimenti, invia il messaggio a tutti i client
                broadcast(msg, name + ": ")
    except OSError as e:
        print(f"Errore nella gestione del client: {e}")
    finally:
        # Rimuove il client dalla lista dei client connessi se non è già stato rimosso
        if client in clients:
            del clients[client]
            update_user_list()  # Aggiorna la lista degli utenti

def broadcast(msg, prefix=""):
    """
    Funzione per inviare messaggi a tutti i client.
    Aggiunge un prefisso opzionale al messaggio.
    """
    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)

def update_user_list():
    """
    Funzione per inviare la lista aggiornata degli utenti a tutti i client.
    """
    user_list = ",".join(clients.values())
    for sock in clients:
        sock.send(bytes(f"/userlist {user_list}", "utf8"))

clients = {}  # Dizionario per memorizzare i client e i loro nomi
ipAddress = {}  # Dizionario per memorizzare gli indirizzi IP dei client

HOST = ''  # Accetta connessioni da qualsiasi interfaccia di rete
PORT = 1606
BUFSIZ = 1024
ADDR = (HOST, PORT)

# Creazione del socket del server
server = socket(AF_INET, SOCK_STREAM)
# Binding del socket all'indirizzo e porta specificati
server.bind(ADDR)

if __name__ == "__main__":
    # Il server inizia ad ascoltare le connessioni in entrata
    server.listen(5)
    print("Server in attesa di connessioni...")
    # Avvia il thread per gestire le connessioni in entrata
    ACCEPT_THREAD = Thread(target=manageIncomingConnections)
    ACCEPT_THREAD.start()
    # Attende che il thread termini
    ACCEPT_THREAD.join()
    # Chiude il server dopo che il thread ha terminato
    server.close()
