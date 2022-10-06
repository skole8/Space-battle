import pygame
import sys  # ukljucivanje pygame modula
import os
from pygame import mixer  # ukljucivanje mixera za zvucne efekte
import random  # ukljucivanje klase za generisanje nasumicnih brojeva
import threading  # ukljucivanje multithreadinga
pygame.init()  # inicijalizacija pygame modula
pygame.font.init()
pygame.mixer.init()
mixer.music.load("background.mp3")  # Ucitavanje i pustanje background muzike
mixer.music.play(-1)

WIDTH = 900  # Definisanje sirine i visine
HEIGHT = 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # kreiranje površine odnosno prozora igrice
pygame.display.set_caption("Space battle")  # postavljanje naslova prozora
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # definisanje nekih osnovnih boja koje će nam biti potrebne
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

FONT = pygame.font.SysFont("comicsans", 40)  # definisanje fonta
SPACE_IMAGE = pygame.image.load(os.path.join('background.png'))
SPACE_IMAGE = pygame.transform.scale(SPACE_IMAGE, (WIDTH, HEIGHT))
SPACESHIP_IMAGE = pygame.image.load(os.path.join('space_ship.png'))
SPACESHIP_IMAGE = pygame.transform.scale(SPACESHIP_IMAGE, (55, 40))
SPACESHIP_IMAGE_LEFT = pygame.transform.rotate(SPACESHIP_IMAGE, 90)
SPACESHIP_IMAGE_RIGHT = pygame.transform.rotate(SPACESHIP_IMAGE, 270)
BOOSTER_IMAGE = pygame.image.load(os.path.join('booster.png'))   # ucitavanje slika koje ce nam biti potrebne
BOOSTER_IMAGE = pygame.transform.scale(BOOSTER_IMAGE, (40, 40))
ASTEROID_IMAGE = pygame.image.load(os.path.join('asteroid.png'))
ASTEROID_IMAGE = pygame.transform.scale(ASTEROID_IMAGE, (80, 80))
ASTEROID_IMAGE.set_colorkey(BLACK)
ASTEROID_IMAGE.set_alpha(512)  # podesavanje transparentnosti slike asteroida
ASTEROID_IMAGE.convert_alpha()

LEFT_HIT = pygame.USEREVENT + 1  # definisanje EVENTA za pogotke
RIGHT_HIT = pygame.USEREVENT + 2
left_damage = 1
right_damage = 1  # neke globalne varijable koje su nam potrebne
speed = 2
speed1 = 2


def move_objects(asteroid, asteroid1, booster):  # funkcija za pomjeranje asteroida i boostera po ekranu
    global speed
    global speed1
    if asteroid.y > 600:
        asteroid.y = -(random.randrange(20, 500, 10))
        asteroid.x = random.randrange(WIDTH//2 - 200, WIDTH//2 + 150, 35)
        speed = random.randrange(1, 5, 1)
    if asteroid1.y > 600:       # pomjeranje asteroida
        asteroid1.y = -(random.randrange(20, 500, 10))
        asteroid1.x = random.randrange(WIDTH // 2 - 200, WIDTH // 2 + 150, 35)
        speed1 = random.randrange(1, 5, 1)
    if booster.y < 0:
        if random.randrange(1, 500, 1) == 5:
            booster.x = random.randrange(200, WIDTH-200, 10)        # pomjeranje boostera
            booster.y = random.randrange(100, HEIGHT-100, 10)
    asteroid.y += speed
    asteroid1.y += speed1


def draw_winner(text):  # funkcija koja prikazuje pobjednika i restartuje igru
    draw_text = FONT.render(text, True, WHITE)
    WIN.blit(draw_text, (300, 200))
    text = FONT.render("Press SPACE to start new game", True, WHITE)
    WIN.blit(text, (180, 400))
    pygame.display.update()
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()      # detektovanje izlaska i pritiska na space za restartovanje igre
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                match_start()


def draw_window(left, right, left_bullets, right_bullets, left_health, right_health, asteroid, asteroid1, booster):
    WIN.blit(SPACE_IMAGE, (0, 0))
    left_health_text = FONT.render("Health: " + str(left_health), True, WHITE)
    right_health_text = FONT.render("Health: " + str(right_health), True, WHITE)
    pygame.draw.rect(WIN, GREEN, booster)
    WIN.blit(BOOSTER_IMAGE, (booster.x, booster.y))
    WIN.blit(left_health_text, (20, 20))
    WIN.blit(right_health_text, (700, 20))
    WIN.blit(SPACESHIP_IMAGE_LEFT, (left.x, left.y))        # funkcija za osjvežavanje ekrana
    WIN.blit(SPACESHIP_IMAGE_RIGHT, (right.x, right.y))
    WIN.blit(ASTEROID_IMAGE, (asteroid.x, asteroid.y))
    WIN.blit(ASTEROID_IMAGE, (asteroid1.x, asteroid1.y))
    for bullet in left_bullets:
        pygame.draw.rect(WIN, RED, bullet)
    for bullet in right_bullets:
        pygame.draw.rect(WIN, BLUE, bullet)
    pygame.display.update()


def left_movement(keys_pressed, left):
    if keys_pressed[pygame.K_a] and left.x > 0:
        left.x -= 3
    if keys_pressed[pygame.K_d] and left.x < 440:
        left.x += 3             # funkcija za realizovanje kretnje lijevog igraca
    if keys_pressed[pygame.K_w] and left.y > 0:
        left.y -= 3
    if keys_pressed[pygame.K_s] and left.y < 440:
        left.y += 3


def right_movement(keys_pressed, right):
    if keys_pressed[pygame.K_LEFT] and right.x > 460:
        right.x -= 3
    if keys_pressed[pygame.K_RIGHT] and right.x < 863:      # funkcija za realizovanje kretnje desnog igraca
        right.x += 3
    if keys_pressed[pygame.K_UP] and right.y > 0:
        right.y -= 3
    if keys_pressed[pygame.K_DOWN] and right.y < 440:
        right.y += 3


def handle_bullets(left_bullets, right_bullets, left, right, asteroid, asteroid1, booster):
    global left_damage
    global right_damage
    collision_sound = mixer.Sound("collision.mp3")
    for bullet in left_bullets:     # logika metaka za lijevog igraca
        bullet.x += 6
        if asteroid.colliderect(bullet) or asteroid1.colliderect(bullet):
            collision_sound.play()
            left_bullets.remove(bullet)
            left_damage = 1
        if right.colliderect(bullet):
            collision_sound.play()
            pygame.event.post(pygame.event.Event(RIGHT_HIT))
            left_bullets.remove(bullet)
        elif bullet.x > 900:
            left_bullets.remove(bullet)
            left_damage = 1
        if booster.colliderect(bullet):
            collision_sound.play()
            left_bullets.remove(bullet)
            booster.y = -50
            left_damage = 2

    for bullet in right_bullets:    # logika metaka za desnog igraca
        bullet.x -= 6
        if asteroid.colliderect(bullet) or asteroid1.colliderect(bullet):
            collision_sound.play()
            right_bullets.remove(bullet)
            right_damage = 1
        if left.colliderect(bullet):
            collision_sound.play()
            pygame.event.post(pygame.event.Event(LEFT_HIT))
            right_bullets.remove(bullet)
        elif bullet.x < 0:
            right_bullets.remove(bullet)
            right_damage = 1
        if booster.colliderect(bullet):
            collision_sound.play()
            right_bullets.remove(bullet)
            booster.y = -50
            right_damage = 2


def handle_collisions(left, right, asteroid, asteroid1):    # funkcija za logiku sudaranja asteroida i brodova
    collision_sound = mixer.Sound("collision.mp3")
    if left.colliderect(asteroid):
        collision_sound.play()
        asteroid.y = 500
        pygame.event.post(pygame.event.Event(LEFT_HIT))
    elif left.colliderect(asteroid1):
        collision_sound.play()
        asteroid1.y = 500
        pygame.event.post(pygame.event.Event(LEFT_HIT))
    if right.colliderect(asteroid):
        collision_sound.play()
        pygame.event.post(pygame.event.Event(RIGHT_HIT))
        asteroid.y = 500
    elif right.colliderect(asteroid1):
        collision_sound.play()
        pygame.event.post(pygame.event.Event(RIGHT_HIT))
        asteroid1.y = 500


def match_start():
    left = pygame.Rect(100, 300, 55, 40)
    right = pygame.Rect(800, 300, 55, 40)   # definisanje potrebnih pravugaonika
    asteroid = pygame.Rect(300, -250, 70, 70)
    asteroid1 = pygame.Rect(550, -350, 70, 70)
    booster = pygame.Rect(-50, -50, 30, 30)
    clock = pygame.time.Clock()
    run = True
    left_bullets = []
    right_bullets = []  # liste za metkove
    left_health = 10
    right_health = 10   # health za brodove
    global left_damage  # globalne varijable za damage
    global right_damage
    button_press_time_left = 0  # promjenjive koje ce da koriste za ulti cooldown
    button_press_time_right = 0
    bullet_sound = mixer.Sound("fire.mp3")
    while run:  # glavna petlja igrice
        clock.tick(60)  # postavljanje FPS
        current_time = pygame.time.get_ticks()  # proteklo vrijeme od starta programa
        for event in pygame.event.get():  # prolazak kroz eventove u programu
            if event.type == pygame.QUIT:  # detektovanje QUIT eventa
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:    # detektovanje pritiska na dugme
                if event.key == pygame.K_LCTRL and len(left_bullets) < 3:
                    bullet = pygame.Rect(left.x + left.width, left.y + 20, 20, 10)
                    left_bullets.append(bullet)                # realizacija pucanja na CTRL
                    bullet_sound.play()
                if event.key == pygame.K_RCTRL and len(right_bullets) < 3:
                    bullet = pygame.Rect(right.x, right.y + 20, 20, 10)
                    right_bullets.append(bullet)
                    bullet_sound.play()
                if event.key == pygame.K_c:
                    if current_time - button_press_time_left >= 8000:
                        bullet1 = pygame.Rect(left.x + left.width, left.y - 40, 20, 10)
                        bullet2 = pygame.Rect(left.x + left.width, left.y, 20, 10)
                        bullet3 = pygame.Rect(left.x + left.width, left.y + 40, 20, 10)
                        left_bullets.append(bullet1)
                        left_bullets.append(bullet2)
                        left_bullets.append(bullet3)
                        button_press_time_left = pygame.time.get_ticks()          # realizacija ulti move
                if event.key == pygame.K_l:
                    if current_time - button_press_time_right >= 8000:
                        bullet1 = pygame.Rect(right.x + right.width, right.y - 40, 20, 10)
                        bullet2 = pygame.Rect(right.x + right.width, right.y, 20, 10)
                        bullet3 = pygame.Rect(right.x + right.width, right.y + 40, 20, 10)
                        right_bullets.append(bullet1)
                        right_bullets.append(bullet2)
                        right_bullets.append(bullet3)
                        button_press_time_right = pygame.time.get_ticks()
            if event.type == LEFT_HIT:
                left_health -= 1 * right_damage
                right_damage = 1
            if event.type == RIGHT_HIT:                 # detektovanje hit eventova
                right_health -= 1 * left_damage
                left_damage = 1
        keys_pressed = pygame.key.get_pressed()
        left_movement(keys_pressed, left)       # pozivanje bitnih funkcija
        right_movement(keys_pressed, right)
        handle_bullets(left_bullets, right_bullets, left, right, asteroid, asteroid1, booster)
        t1 = threading.Thread(target=move_objects, args=(asteroid, asteroid1, booster, ))
        t1.setDaemon = True         # paralelizacija
        t1.start()
        handle_collisions(left, right, asteroid, asteroid1)
        draw_window(left, right, left_bullets, right_bullets, left_health, right_health, asteroid, asteroid1, booster)
        if left_health <= 0:    # provjera da li je nekom igracu health pao na 0
            draw_winner("Right player win!")
            run = False
        if right_health <= 0:
            draw_winner("Left player win!")
            run = False


def main():  # pocetni meni
    WIN.blit(SPACE_IMAGE, (0, 0))  # lijepljenje background slike na povrsinu

    font = pygame.font.SysFont("comicsans", 40)
    title = font.render("SPACE BATTLE", True, WHITE)
    WIN.blit(title, (WIDTH / 2 - 150, 10))
    start_game_text = font.render("Press SPACE to start the game", True, WHITE)
    WIN.blit(start_game_text, (WIDTH / 2 - 280, HEIGHT - 100))

    font = pygame.font.SysFont("comicsans", 30)
    text = FONT.render("Left controls:", True, WHITE)
    WIN.blit(text, (20, 100))

    text = font.render("Movement: W,A,S,D", True, WHITE)  # ispisivanje teksta pocetnog menija
    WIN.blit(text, (20, 180))

    text = font.render("Shooting: LEFT CTRL", True, WHITE)
    WIN.blit(text, (20, 220))

    text = font.render("Ulti: C", True, WHITE)
    WIN.blit(text, (20, 260))

    controls = FONT.render("Right controls:", True, WHITE)
    WIN.blit(controls, (WIDTH - 350, 100))

    text = font.render("Movement: Arrow keys", True, WHITE)
    WIN.blit(text, (WIDTH - 350, 180))

    text = font.render("Shooting: RIGHT CTRL", True, WHITE)
    WIN.blit(text, (WIDTH - 350, 220))

    text = font.render("Ulti: L", True, WHITE)
    WIN.blit(text, (WIDTH - 350, 260))

    pygame.display.update()  # azuriranje ekrana
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:  # detektovanje izlaska iz igre
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # pokretanje igre kada se pritisne space dugme
                match_start()


if __name__ == "__main__":  # komanda kojom se obezbjeđuje da se main funkcija izvrši
    main()                  # ukoliko se ova skripta direktno pokrene
