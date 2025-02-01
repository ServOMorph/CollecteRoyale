import socket
import threading

host = '127.0.0.1'
port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen()

print("Serveur en attente de connexions...")

# Variables pour suivre les joueurs
nb_joueurs = 0
liste_joueurs = []
clients = []
lock = threading.Lock()

def gerer_client(conn, addr):
    global nb_joueurs, liste_joueurs
    print(f"Nouvelle connexion : {addr}")
    buffer = ""
    nom_joueur = None

    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                if message.lower().startswith("nom du joueur = "):
                    base_nom = message.split("=", 1)[1].strip()
                    with lock:
                        # Vérifier si le nom existe déjà et le modifier si nécessaire
                        nom_joueur = base_nom
                        compteur = 1
                        while nom_joueur in liste_joueurs:
                            nom_joueur = f"{base_nom}_{compteur}"
                            compteur += 1
                        liste_joueurs.append(nom_joueur)
                        nb_joueurs += 1
                    
                    print(f"Joueur connecté : {nom_joueur}")
                    print(f"Nombre de joueurs connectés : {nb_joueurs}")
                    # Envoyer la confirmation au client
                    conn.send(f"Bienvenue {nom_joueur}, joueurs en ligne: {nb_joueurs}\n".encode())
                    envoyer_a_tous(f"{nom_joueur} a rejoint la partie. Joueurs en ligne: {nb_joueurs}")

    except Exception as e:
        print(f"Erreur avec {addr}: {e}")
    # Déconnexion du client
    print(f"Déconnexion de {addr}")

    # Le bloc `finally` est maintenant bien structuré
    print(f"Déconnexion de {addr}")
    with lock:
        if nom_joueur and nom_joueur in liste_joueurs:
            liste_joueurs.remove(nom_joueur)
            nb_joueurs -= 1
            envoyer_a_tous(f"{nom_joueur} a quitté la partie. Joueurs restants: {nb_joueurs}")
        if conn in clients:
            clients.remove(conn)
        conn.close()

def envoyer_a_tous(message):
    with lock:
        deconnectes = []
        for client in clients:
            try:
                client.send(f"{message}\n".encode())
            except:
                deconnectes.append(client)  # Ajouter à une liste pour suppression

        # Retirer proprement les clients déconnectés
        for client in deconnectes:
            clients.remove(client)
            client.close()

while True:
    conn, addr = server_socket.accept()
    with lock:
        clients.append(conn)  # Ajout sécurisé
    thread = threading.Thread(target=gerer_client, args=(conn, addr), daemon=True)
    thread.start()
