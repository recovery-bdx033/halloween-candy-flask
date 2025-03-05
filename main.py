import pygame
import random
#######import serial  # Gestion de la connexion série
import os #pour gestion des records
import sys  # Pour fermer proprement le programme


# Initialisation de Pygame
pygame.init()

# Initialisation du module de son
pygame.mixer.init()

# Constantes de la fenêtre
WIDTH, HEIGHT = 900, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Halloween Candy Collector V1.2 par HBD") 

# Couleurs RGB
BLACK = (25, 25, 70)#easy
WHITE = (255, 255, 255)
RED = (190, 3, 30)  # Fin de partie
GREEN = (0,200, 0)  # Victoire
BLUE = (0,255,255)
PINK = (250,20,120)

volume = 0.5  # Volume initial (entre 0.0 et 1.0)


# Chargement des images
player_img = pygame.image.load("player.png")  # Image du personnage
candy_img = pygame.image.load("candy.png")  # Image des bonbons
obstacle_img = pygame.image.load("ghost.png")  # Image d'un obstacle
witch_img = pygame.image.load("witch.png")  # Image d'une sorcière
background_img = pygame.image.load("background.png")  # Image de fond pour le menu
boy_img = pygame.image.load("player.png")  # Image du garçon
girl_img = pygame.image.load("player2.png")  # Image de la fille (remplace avec le bon chemin)
background2_img = pygame.image.load("background2.png")  # Image de fond pour le menu

# Chargement des sons
sound_candy = pygame.mixer.Sound("candy.wav")  # Son quand un bonbon est collecté
sound_witch = pygame.mixer.Sound("witch.wav")  # Son quand on touche une sorcière
sound_ghost = pygame.mixer.Sound("ghost.wav")  # Son quand on touche un fantôme
sound_hurlement = pygame.mixer.Sound("hurlement.wav")  # Son quand on touche un fantôme
sound_record = pygame.mixer.Sound("record.wav")  # Record
sound_victoire = pygame.mixer.Sound("victoire.wav")  # victoire

# Charger la musique de fond
pygame.mixer.music.load("halloween.wav")  # Remplace par le nom de ton fichier .wav
pygame.mixer.music.set_volume(volume)  # Ajuste le volume selon ton besoin
pygame.mixer.music.play(-1)  # -1 signifie "jouer en boucle infinie"

# Redimensionnement des images
player_img = pygame.transform.scale(player_img, (50, 50))
candy_img = pygame.transform.scale(candy_img, (30, 30))
obstacle_img = pygame.transform.scale(obstacle_img, (40, 40))
witch_img = pygame.transform.scale(witch_img, (50, 50))
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
background2_img = pygame.transform.scale(background2_img, (WIDTH, HEIGHT))
boy_img = pygame.transform.scale(boy_img, (50, 50))
girl_img = pygame.transform.scale(girl_img, (50, 50))

score_color = WHITE
score_color_timer = 0 # timer pour passer le score en vert quand on attrape un bonbon
hit_by_witch_timer = 0  # Timer pour le fond rouge

# Valeur par défaut des records absolus
record_easy = 0
record_hard = 0
record_easy_player = "Personne"
record_hard_player = "Personne"
player_name = "Inconnu"  # Valeur par défaut en cas de problème


# Configuration de la connexion avec l'Arduino sur le port disponible
# arduino = None
# for port in ['/dev/ttyACM0', '/dev/ttyACM1']:
#     try:
#         arduino = serial.Serial(port, 9600, timeout=1)
#         print(f"Connexion établie avec l'Arduino sur {port}")
#         break
#     except Exception as e:
#         print(f"Erreur lors de la connexion à l'Arduino sur {port} : {e}")
# 
# def envoyer_bonbons_arduino(n):
#     """Envoie le nombre de bonbons gagnés à l'Arduino."""
#     if arduino:
#         try:
#             arduino.write(f"{n}\n".encode())  # Envoie 'N' suivi d'un saut de ligne
#             print(f"Envoyé à l'Arduino : {n} bonbons")
#         except Exception as e:
#             print(f"Erreur lors de l'envoi à l'Arduino : {e}")
#     else:
#         print("Aucune connexion Arduino établie.")

# Fonction de sélection de difficulté
def set_difficulty(mode):
    if mode == "easy":
        return 40, 50, 100  # Fréquences normales
    elif mode == "hard":
        return 40, int(50 * 1/4), int(100 * 1/5)  # Plus de fantômes et sorcières

# Sélection du mode
difficulty = "easy"  # Par défaut

# Joueur
player = pygame.Rect(WIDTH//2, HEIGHT - 60, 50, 50)
player_speed = 5

# Bonbons et obstacles
candies = []
obstacles = []
witches = []
candy_spawn_timer, obstacle_spawn_timer, witch_spawn_timer = set_difficulty(difficulty)
candy_score = 0

# Temps limite
game_time = 30 * 30  # 30 secondes en frames (30 FPS)

# Police
font = pygame.font.Font(None, 45)

going = True
clock = pygame.time.Clock()
game_over = False
frame_count = 0


def choisir_personnage():
    global player_name  

    screen.blit(background2_img, (0, 0))

    # Définition des couleurs
    BLUE = (0, 100, 255)
    PINK = (255, 105, 180)
    WHITE = (255, 255, 255)

    # Texte des personnages
    font = pygame.font.Font(None, 50)  # Police du texte
    boy_text = font.render("<< F1 - Max", True, BLUE)
    girl_text = font.render("F2 - Zoé >>", True, PINK)

    # Positions des textes
    x_boy, y_boy = WIDTH // 2 - 85, HEIGHT // 2 - 30
    x_girl, y_girl = WIDTH // 2 - 85, HEIGHT // 2 + 30

    # Création des rectangles autour des textes (avec un petit padding)
    padding_x, padding_y = 10, 5
    rect_boy = boy_text.get_rect(topleft=(x_boy, y_boy))
    rect_girl = girl_text.get_rect(topleft=(x_girl, y_girl))

    # Agrandir les rectangles pour bien entourer le texte
    rect_boy.inflate_ip(padding_x * 2, padding_y * 2)
    rect_girl.inflate_ip(padding_x * 2, padding_y * 2)

    # Dessiner des rectangles blancs derrière le texte
    pygame.draw.rect(screen, WHITE, rect_boy)  # Fond blanc
    pygame.draw.rect(screen, WHITE, rect_girl)

    # Affichage des textes par-dessus le fond blanc
    screen.blit(boy_text, (x_boy, y_boy))
    screen.blit(girl_text, (x_girl, y_girl))

    pygame.display.flip()

    # Attente du choix du joueur
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    player_name = "Max"
                    pygame.mixer.music.stop()  # Arrêter la musique du menu
                    waiting = False
                if event.key == pygame.K_F2:
                    player_name = "Zoé"
                    pygame.mixer.music.stop()  # Arrêter la musique du menu
                    waiting = False

    # 🎵 Démarrer la musique du jeu (grotte.wav) en boucle
    pygame.mixer.music.load("grotte.wav")
    pygame.mixer.music.set_volume(0.6)  # Réduit le volume pour ne pas couvrir les autres sons
    pygame.mixer.music.play(-1)  # -1 signifie en boucle infinie

    return boy_img if player_name == "Max" else girl_img



# Menu de sélection
def draw_menu():
    screen.blit(background_img, (0, 0))

    # Création des textes
    easy_text = font.render("Press F1 = Easy", True, GREEN)
    hard_text = font.render("Press F2 = Hard", True, RED)

    # Récupération de la taille des textes
    easy_rect = easy_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 30))
    hard_rect = hard_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 30))

    # Dessiner un rectangle blanc derrière les textes
    pygame.draw.rect(screen, WHITE, easy_rect.inflate(20, 10))  # Surligne "Easy"
    pygame.draw.rect(screen, WHITE, hard_rect.inflate(20, 10))  # Surligne "Hard"

    # Afficher les textes au-dessus du rectangle blanc
    screen.blit(easy_text, easy_rect.topleft)
    screen.blit(hard_text, hard_rect.topleft)

    pygame.display.flip()

draw_menu()# le joueur choisit la diffculté
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_1, pygame.K_KP1, pygame.K_F1]:
                difficulty = "easy"
                waiting = False
            if event.key in [pygame.K_2, pygame.K_KP2, pygame.K_F2]:
                difficulty = "hard"
                waiting = False

candy_spawn_timer, obstacle_spawn_timer, witch_spawn_timer = set_difficulty(difficulty)

player_img = choisir_personnage()  # Le joueur choisit son personnage

def charger_records():
    global record_easy, record_easy_player, record_hard, record_hard_player
    try:
        with open("records.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
            record_easy, record_easy_player = lines[0].strip().split(",")
            record_hard, record_hard_player = lines[1].strip().split(",")
            record_easy = int(record_easy)
            record_hard = int(record_hard)
    
    except (FileNotFoundError, IndexError, ValueError):
        # Valeurs par défaut
        record_easy, record_easy_player = 0, "Personne"
        record_hard, record_hard_player = 0, "Personne"
        sauvegarder_records()  # Création du fichier avec ces valeurs


def sauvegarder_records():
    with open("records.txt", "w", encoding="utf-8") as file:
        file.write(f"{record_easy},{record_easy_player}\n")
        file.write(f"{record_hard},{record_hard_player}\n")


def afficher_game_over():
    screen.fill(RED)  # Fond rouge pour Game Over
    
    game_over_text = font.render("GAME OVER!", True, WHITE)
    retry_text = font.render("Try Again!", True, WHITE)

    # Calcul du positionnement pour être bien centré
    game_over_x = WIDTH // 2 - game_over_text.get_width() // 2
    game_over_y = HEIGHT // 2 - game_over_text.get_height() // 2 - 40  # Décalage vers le haut
    
    retry_x = WIDTH // 2 - retry_text.get_width() // 2
    retry_y = HEIGHT // 2 - retry_text.get_height() // 2 + 40  # Décalage en dessous de "GAME OVER!"

    # Affichage du texte
    screen.blit(game_over_text, (game_over_x, game_over_y))
    screen.blit(retry_text, (retry_x, retry_y))

    pygame.display.flip()
    pygame.time.delay(3000)  # Pause de 3 secondes avant de quitter

###########
charger_records()  # Charger le record au lancement
###############

# Boucle principale
while going:
    if game_over:
        afficher_game_over()
        break
    # Changer l'écran en rouge si le joueur a été touché par une sorcière récemment
    if hit_by_witch_timer and pygame.time.get_ticks() - hit_by_witch_timer < 300:
        screen.fill(RED)  # Écran rouge pendant 300 ms
    else:
         # Changer la couleur de fond selon la difficulté
        if difficulty == "hard":
            screen.fill((25, 25, 25))  # Fond + foncé en mode hard
        else:
            screen.fill(BLACK)  # Fond noir en mode easy
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Si on ferme la fenêtre
            going = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  # Si on appuie sur Échap
            going = False

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            going = False
    
    # Remet le score en blanc après 1 seconde si un bonbon ou une sorcière a été touché
    if score_color_timer > 0 and pygame.time.get_ticks() - score_color_timer > 1000:
        score_color = WHITE  # Remet le texte en blanc
        score_color_timer = 0  # Réinitialise le timer

    
    # Déplacement du joueur
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.x > 0:
        player.x -= player_speed
    if keys[pygame.K_RIGHT] and player.x < WIDTH - player.width:
        player.x += player_speed
    
    # Apparition des bonbons
    if frame_count % candy_spawn_timer == 0:
        candies.append(pygame.Rect(random.randint(0, WIDTH-30), 0, 30, 30))
    
    # Apparition des obstacles
    if frame_count % obstacle_spawn_timer == 0:
        obstacles.append(pygame.Rect(random.randint(0, WIDTH-40), 0, 40, 40))
    
    # Apparition des sorcières
    if frame_count % witch_spawn_timer == 0:
        witches.append(pygame.Rect(random.randint(0, WIDTH-50), 0, 50, 50))
    
    # Déplacement des bonbons
    candy_speed = 1 if difficulty == 'easy' else 2  # Ralentissement en mode easy
    obstacle_speed = 2 if difficulty == 'easy' else 4  # Ralentissement en mode easy
    witch_speed = 1 if difficulty == 'easy' else 2  # Ralentissement en mode easy
    for candy in candies[:]:
        candy.y += candy_speed
        if candy.colliderect(player):
            candies.remove(candy)
            candy_score += 1  # Incrémentation du score lorsque le joueur attrape un bonbon
            score_color = GREEN  # Score en vert
            score_color_timer = pygame.time.get_ticks()  # Enregistre le temps actuel
            sound_candy.play()  # Joue le son du bonbon collecté
        elif candy.y > HEIGHT:
            candies.remove(candy)
    for candy in candies[:]:
        candy.y += 4
        if candy.y > HEIGHT:
            candies.remove(candy)
    
    # Déplacement des obstacles
    for obstacle in obstacles[:]:
        obstacle.y += obstacle_speed
        if obstacle.colliderect(player):
            game_over = True  # Fin du jeu si le joueur touche un fantôme
            sound_ghost.play()  # Joue le son du fantôme touché
            sound_hurlement.play()  # 
        elif obstacle.y > HEIGHT:
            obstacles.remove(obstacle)
    for obstacle in obstacles[:]:
        obstacle.y += 6
        if obstacle.y > HEIGHT:
            obstacles.remove(obstacle)
    
    # Déplacement des sorcières
    for witch in witches[:]:
        witch.y += witch_speed
        if witch.colliderect(player):
            candy_score = max(0, candy_score - 1)  # Réduit le score mais ne descend pas en dessous de 0  # Fin du jeu si le joueur touche une sorcière
            hit_by_witch_timer = pygame.time.get_ticks()  # Démarre le timer de l'écran rouge
            sound_witch.play()  # Joue le son de la sorcière touchée
        elif witch.y > HEIGHT:
            witches.remove(witch)
    for witch in witches[:]:
        witch.y += 3
        if witch.y > HEIGHT:
            witches.remove(witch)
    
    # Affichage
    # Affichage du score et du temps restant
    # Mise à jour du texte avec la couleur dynamique du score
    score_text = font.render(f"Bonbons: {candy_score}", True, score_color)  # Utilise score_color
    time_text = font.render(f"Temps: {game_time // 30} sec", True, WHITE)

    # Affichage du texte à l'écran
    record_easy_text = font.render(f"Record Easy: {record_easy} bonbons ({record_easy_player})", True, WHITE)
    record_hard_text = font.render(f"Record Hard: {record_hard} bonbons ({record_hard_player})", True, WHITE)

    screen.blit(record_easy_text, (10, 70))  # En haut à gauche
    screen.blit(record_hard_text, (10, 100))  # Juste en dessous

   ###################
    screen.blit(score_text, (10, 10))
    screen.blit(time_text, (10, 40))
    screen.blit(player_img, (player.x, player.y))
    for candy in candies:
        screen.blit(candy_img, (candy.x, candy.y))
    for obstacle in obstacles:
        screen.blit(obstacle_img, (obstacle.x, obstacle.y))
    for witch in witches:
        screen.blit(witch_img, (witch.x, witch.y))
    
    pygame.display.flip()
    clock.tick(35)
    game_time -= 1
    frame_count += 1
    
  ##################################  # Fin de la partie après 30 secondes##################################
    if game_time <= 0:
        record_battu = False  # Flag pour savoir si un record est battu

        if difficulty == "easy":
            if candy_score > record_easy:
                sound_record.play()
                record_easy = candy_score
                record_easy_player = player_name
                sauvegarder_records()
                record_battu = True  # Active le flag

        else:  # Mode Hard
            if candy_score > record_hard:
                sound_record.play()
                record_hard = candy_score
                record_hard_player = player_name
                sauvegarder_records()
                record_battu = True  # Active le flag

        # Gestion du fond et du message
        if candy_score == 0:
            screen.fill(BLACK)
            message = ["Essaie à nouveau!"]
        else:
            screen.fill(GREEN)
            message = ["BRAVO! Tu as gagné {} bonbons!".format(candy_score)]
            if record_battu:
                message.insert(0, "BRAVO! RECORD BATTU!")  # Ajoute le message du record en premier

            sound_victoire.play()
 ##web####  envoyer_bonbons_arduino(candy_score)

        # Affichage du texte
        y_offset = HEIGHT // 2
        for line in message:
            text_surface = font.render(line, True, WHITE)
            screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, y_offset))
            y_offset += 50

        pygame.display.flip()
        pygame.time.delay(6000)
        break


   
    
pygame.quit()
sys.exit()  # Ferme proprement l'exécutable












