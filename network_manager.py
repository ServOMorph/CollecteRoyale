import uuid
import socket
import pygame   
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox
import math
import random
import subprocess

host = '127.0.0.1'
port = 12345

buffer = ""
client_socket = None
server_online = False
display_window_connect = True
player_name = ""
client_connected = False

print("Chargement de network_manager")

def attendre_serveur_en_thread():
    """Essaye de se connecter au serveur en arrière-plan et met à jour `server_online`."""
    global server_online, client_socket

    while not server_online:
        try:
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket.connect((host, port))
            print("Connexion au serveur réussie.")
            server_online = True
            client_socket = temp_socket  # On garde la connexion réussie
            
            # Lancer l'écoute des messages après la connexion réussie
            thread_reception = threading.Thread(target=listen_for_messages, daemon=True)
            thread_reception.start()
            
            return  # Sort de la boucle après connexion réussie
        except (ConnectionRefusedError, OSError):
            print("Le serveur n'est pas en ligne. Nouvelle tentative dans 3 secondes...")
            time.sleep(3)  # Attendre avant de réessayer

def listen_for_messages():
    """Écoute les messages du serveur en continu."""
    global buffer, display_window_connect
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                sys.stdout.write(f"\rServeur: {message}\n")
                sys.stdout.flush()
                # Vérifie si le message contient le nombre de joueurs
                if "Joueurs en ligne" in message:
                    try:
                        nbr_joueurs = int(message.split()[-1])  # Extraction du nombre de joueurs
                        print(f"nbr de joueur = {nbr_joueurs}")
                        display_window_connect = False
                        if nbr_joueurs == 2:
                            print("\nDeux joueurs connectés, lancement du jeu...")
                    except ValueError:
                        pass  # Ignore si l'extraction échoue
        except Exception as e:
            print(f"Erreur lors de la réception des messages: {e}")
            break

def connect_to_server(player_name):
    global client_socket, client_connected
    while not client_connected:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            print(f"Connecté au serveur avec le nom : {player_name}")
            # Envoi automatique du nom du joueur
            message = f"Nom du joueur = {player_name}\n"
            client_socket.send(message.encode())
            client_connected = True
        except (ConnectionRefusedError, OSError):
            print("Le serveur n'est pas en ligne. Nouvelle tentative dans 3 secondes...")
            time.sleep(3)  # Attente avant nouvelle tentative
    # Lancer un thread pour écouter les messages du serveur
    thread_reception = threading.Thread(target=listen_for_messages, daemon=True)
    thread_reception.start()
    while True:
        pass

def fast_connect():
    global client_socket
    player_name = f"Joueur_{uuid.uuid4().hex[:6]}"
    connect_to_server(player_name)
   
def connect_normal():
    print("Lancement de connect_normal dans network_manager")
    global client_socket, server_online, player_name, client_connected
    
    # Lancer l’attente serveur en arrière-plan
    thread_serveur = threading.Thread(target=attendre_serveur_en_thread, daemon=True)
    thread_serveur.start()

    # Initialisation du mixer
    pygame.mixer.init()

    # Couleurs
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (100, 100, 100)
    RED = (220, 20, 60)
    VERT = (173, 227, 16) 

    global display_window_connect, server_online

    input_active = False
    client_socket = None
   
    #Coordonnée des zones cliquable
    quit_zone_x, quit_zone_y, quit_zone_w, quit_zone_h = 600, 720, 157, 64 # Quit
    quit_zone2_x, quit_zone2_y, quit_zone2_w, quit_zone2_h = 483, 775, 192, 69 # Quit2

    connect_zone_x, connect_zone_y, connect_zone_w, connect_zone_h = 357, 537, 231, 50 # Connect
    
    # Dimensions de la fenêtre
    WIDTH, HEIGHT = 900, 900

    # Initialisation de Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Client ServOMorph")
    pygame.mixer.init()
    pygame.mixer.music.load(r"C:\Users\raph6\Documents\Python\CollecteRoyale\V5\CollecteRoyale\Zic\zic1.mp3")

    # Police
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 36)

    # Fonction pour dessiner un bouton
    def draw_button(text, x, y, w, h, color, text_color):
        pygame.draw.rect(screen, color, (x, y, w, h))
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2))
        screen.blit(text_surface, text_rect)

    pygame.mixer.music.play(loops=-1)

    # Serveur hors ligne
    while not server_online:
        
        background_image2 = pygame.image.load(r"C:\Users\raph6\Documents\Python\CollecteRoyale\V5\CollecteRoyale\Images\interface2.png")
        background_image2 = pygame.transform.scale(background_image2, (WIDTH, HEIGHT))
        screen.blit(background_image2, (0, 0))  # Affiche l'image de fond

        pygame.display.flip()
        time.sleep(0.1)

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Gérer le clic souris
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Vérifie si la zone "Quitter" est cliquée
                if quit_zone2_x <= event.pos[0] <= quit_zone2_x + quit_zone2_w and \
                    quit_zone2_y <= event.pos[1] <= quit_zone2_y + quit_zone2_h:
                    if client_socket:
                        client_socket.close()
                    pygame.quit()
                    sys.exit()

    # Serveur en ligne
    while display_window_connect:
        background_image = pygame.image.load(r"C:\Users\raph6\Documents\Python\CollecteRoyale\V5\CollecteRoyale\Images\interface.png")
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

        screen.blit(background_image, (0, 0))  # Affiche l'image de fond
        
        # Affiche "Nom du joueur"
        name_label = font.render("Nom du joueur :", True, WHITE)
        screen.blit(name_label, (375, 394))

        # Dessine une zone pour entrer le nom
        input_box = pygame.Rect(340, 438, 262, 30)
        pygame.draw.rect(screen, GRAY if input_active else BLACK, input_box)
        pygame.draw.rect(screen, WHITE, input_box, 2)

        # Affiche le texte entré par le joueur, centré dans la zone d'entrée
        name_surface = font.render(player_name, True, WHITE)
        text_width = name_surface.get_width()
        text_x = input_box.x + (input_box.width - text_width) // 2  # Calcul pour centrer
        screen.blit(name_surface, (text_x, input_box.y + 5))

        # Affiche un message de bienvenue
        if 'error_message' in locals() and error_message:
            error_text = font.render(error_message, True, WHITE)
            screen.blit(error_text, (100, 730))

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Gérer le clic souris
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Activer le champ texte
                if input_box.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False

                # Vérifie si la zone "Connect" est cliquée
                if connect_zone_x <= event.pos[0] <= connect_zone_x + connect_zone_w and \
                    connect_zone_y <= event.pos[1] <= connect_zone_y + connect_zone_h:
                    if not client_connected: 
                        if not player_name.strip():
                            error_message = "Entrer le nom du joueur"
                        else:
                            print("affichage msg de bienvenue")
                            welcome_text = font.render(f"Bienvenue {player_name}", True, WHITE)
                            screen.blit(welcome_text, (100,730)) #718
                            pygame.display.flip()
                            client_socket, success = connect_to_server(player_name)
                            if success:
                                error_message = None
                                if not any(thread.name == "thread_reception" for thread in threading.enumerate()):
                                    thread_reception = threading.Thread(target=listen_for_messages, daemon=True, name="thread_reception")
                                    thread_reception.start()

                # Vérifie si la zone "Quitter" est cliquée
                if quit_zone_x <= event.pos[0] <= quit_zone_x + quit_zone_w and \
                    quit_zone_y <= event.pos[1] <= quit_zone_y + quit_zone_h:
                    if client_socket:
                        client_socket.close()
                    pygame.quit()
                    sys.exit()

            # Gérer la saisie clavier
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]  # Supprimer le dernier caractère
                else:
                    player_name += event.unicode  # Ajouter le caractère tapé
        pygame.display.flip()
    
    print("sortie de la boulce while server_online")        
    #pygame.display.quit()
    #print("Fenêtre de connection fermée")
    #launch_game()
        
    def init_game_window():
        pygame.init()
        WIDTH, HEIGHT = 1920, 1080
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Collecte Royale")
        return screen, WIDTH, HEIGHT

    def launch_game():
        screen, WIDTH, HEIGHT = init_game_window()
        print("def launch_game activée, lancement du jeu")

        # Charger les images de fond
        background_image_intro = pygame.image.load(r"C:\Users\raph6\Documents\Python\CollecteRoyale\V5\CollecteRoyale\Images\Collecte Royale.png")
        background_image_intro = pygame.transform.scale(background_image_intro, (WIDTH, HEIGHT))
        background_image_explain = pygame.image.load(r"C:\Users\raph6\Documents\Python\CollecteRoyale\V5\CollecteRoyale\Images\explication du jeu.png")
        background_image_explain = pygame.transform.scale(background_image_explain, (WIDTH, HEIGHT))

        # Barre de progression
        BAR_WIDTH, BAR_HEIGHT = 600, 10
        bar_x = (WIDTH - BAR_WIDTH) // 2
        bar_y = HEIGHT - BAR_HEIGHT - 50
        bar_color = (173, 227, 16)
        border_color = (255, 255, 255)
        border_thickness = 5
        total_duration = 2
        fps = 60
        clock = pygame.time.Clock()

        # Progression
        start_time = time.time()
        while time.time() - start_time < total_duration:
            screen.blit(background_image_intro, (0, 0))
            progress = (time.time() - start_time) / total_duration
            progress_width = int(BAR_WIDTH * progress)
            pygame.draw.rect(screen, border_color, (bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT), border_thickness)
            pygame.draw.rect(screen, bar_color, (bar_x, bar_y, progress_width, BAR_HEIGHT))
            pygame.display.flip()
            clock.tick(fps)

        # Image finale après la progression
        screen.blit(background_image_explain, (0, 0))
        pygame.display.flip()
        time.sleep(5)
        print("Lancement de la suite")
        pygame.display.quit()
        subprocess.Popen(["python", "setup_game.py"])
    """    

    if server_online:
        # Lancer un thread pour écouter les messages du serveur
        thread_reception = threading.Thread(target=listen_for_messages, daemon=True)
        thread_reception.start()

    """  
