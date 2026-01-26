import math
import random
import pygame
from pygame import mixer

# Inicialização
pygame.init()

# --- ÁUDIO (Coloque logo após o pygame.init()) ---
mixer.init()
mixer.music.load("D:\\Space Invodars\\data\\sounds\\Intro.wav")
mixer.music.set_volume(0.070)  # Música de fundo baixinha
mixer.music.play(-1)

# Efeitos Sonoros (Usando mixer.Sound para não parar a música)
explosion_sound = mixer.Sound('D:\\Space Invodars\\data\\sounds\\explosion.wav')
explosion_sound.set_volume(0.1)

laser_sound = mixer.Sound('D:\\Space Invodars\\data\\sounds\\bullet.wav')
laser_sound.set_volume(0.015)

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Invaders - Galaxia Anima")
clock = pygame.time.Clock()

def load_img(path, size=None):
    img = pygame.image.load(path)
    if size: img = pygame.transform.scale(img, size)
    return img

# Recursos
playerImage = load_img('D:\\Space Invodars\\data\\Sprites\\nave_2.png')
bulletImage = load_img('D:\\Space Invodars\\data\\Sprites\\bullet.png')
explosionImage = load_img('D:\\Space Invodars\\data\\Sprites\\explosion.png')
bg_images = [
    load_img('D:\\Space Invodars\\data\\backgrounds\\BG_1.jpg', (800, 600)),
    load_img('D:\\Space Invodars\\data\\backgrounds\\BG_2.png', (800, 600)),
    load_img('D:\\Space Invodars\\data\\backgrounds\\BG_3.png', (800, 600)),
    load_img('D:\\Space Invodars\\data\\backgrounds\\BG_4.png', (800, 600))
]

font = pygame.font.Font('freesansbold.ttf', 20)
big_font = pygame.font.Font('freesansbold.ttf', 64)

# Variáveis de Estado
score_val = 0
level_val = 1
running = True
game_state = "PLAYING" 
transition_timer = 0

game_state = "MENU" 
music_muted = False
effects_muted = False

player_X = 370
player_Y = 523
player_speed = 5

# --- NOVA ESTRUTURA DE ALIENS ---
aliens = [] 

def spawn_aliens(level):
    aliens.clear()
    # Define a quantidade de aliens por fase
    qtd = 6 + (level * 2) 
    speed = 0.8 + (level * 0.5)
    img_path = f'D:\\Space Invodars\\data\\Sprites\\alien_{min(level, 4)}.png'
    
    for i in range(qtd):
        aliens.append({
            "x": random.randint(64, 730),
            "y": random.randint(30, 150),
            "speed": speed if random.random() > 0.5 else -speed,
            "img": load_img(img_path)
        })

spawn_aliens(1)

bullet_X = 0
bullet_Y = 523
bullet_state = "rest"
bullet_speed = 12

exp_X, exp_Y = 0, 0
exp_visible = False
exp_timer = 0

def show_ui():
    score_text = font.render(f"Points: {score_val} | ETs: {len(aliens)}", True, (255, 255, 255))
    level_text = font.render(f"Level: {level_val}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 35))

def is_collision(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2) < 35

def draw_text_centered(text, font, color, y_offset):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(screen_width // 2, y_offset))
    screen.blit(render, rect)

def draw_menu():
    screen.blit(bg_images[0], (0, 0)) # Fundo da fase 1
    
    # Texto da História
    small_f = pygame.font.Font('freesansbold.ttf', 16)
    draw_text_centered("A galaxia ânima foi atacada por uma raça chamada invodars,", small_f, (255, 255, 255), 150)
    draw_text_centered("você é o único que pode parar esta invasão!", small_f, (255, 255, 255), 175)
    
    draw_text_centered("Mova-se utilizando as setinhas do teclado, a medida que passar os níveis estará cada vez", small_f, (255, 255, 255), 220)
    draw_text_centered("E atire com a tecla ESPAÇO", small_f, (255, 255, 255), 245)
    draw_text_centered("mais longe de nosso sistema solar! Acabe com o enxame das naves", small_f, (255, 255, 255), 2270)
    draw_text_centered("para salvar a galaxia ânima!!!", small_f, (255, 255, 255), 295)

    # Opções
    draw_text_centered("Pressione [ENTER] para Iniciar", font, (0, 255, 0), 400)
    draw_text_centered("Pressione [C] para Configurações", font, (255, 255, 255), 450)

def draw_config():
    screen.fill((20, 20, 40))
    draw_text_centered("CONFIGURAÇÕES", big_font, (255, 255, 255), 150)
    
    m_color = (255, 0, 0) if music_muted else (0, 255, 0)
    e_color = (255, 0, 0) if effects_muted else (0, 255, 0)
    
    draw_text_centered(f"[1] Músicas: {'MUTADO' if music_muted else 'LIGADO'}", font, m_color, 300)
    draw_text_centered(f"[2] Efeitos: {'MUTADO' if effects_muted else 'LIGADO'}", font, e_color, 350)
    draw_text_centered("Pressione [ESC] para Voltar", font, (255, 255, 255), 500)

# Loop Principal
# --- LOOP PRINCIPAL ---
while running:
    # 1. Escolha do Background baseado no estado
    if game_state == "MENU" or game_state == "CONFIG":
        screen.blit(bg_images[0], (0, 0)) # Fundo da fase 1 para os menus
    else:
        screen.blit(bg_images[min(level_val-1, 3)], (0, 0))
    
    # 2. SISTEMA DE EVENTOS (TECLADO)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Comandos no Menu Inicial
            if game_state == "MENU":
                if event.key == pygame.K_RETURN: game_state = "PLAYING"
                if event.key == pygame.K_c: game_state = "CONFIG"
            
            # Comandos nas Configurações
            elif game_state == "CONFIG":
                if event.key == pygame.K_1:
                    music_muted = not music_muted
                    mixer.music.set_volume(0 if music_muted else 0.2)
                if event.key == pygame.K_2:
                    effects_muted = not effects_muted
                    explosion_sound.set_volume(0 if effects_muted else 0.7)
                    laser_sound.set_volume(0 if effects_muted else 0.4)
                if event.key == pygame.K_ESCAPE: game_state = "MENU"
            
            # Comando de Pause
            elif game_state == "PLAYING":
                if event.key == pygame.K_p: game_state = "PAUSE"
            
            elif game_state == "PAUSE":
                if event.key == pygame.K_p: game_state = "PLAYING"
            
            # Reiniciar o Jogo
            elif game_state in ["WIN", "GAMEOVER"]:
                if event.key == pygame.K_r:
                    score_val = 0
                    level_val = 1
                    spawn_aliens(1)
                    game_state = "PLAYING"

    keys = pygame.key.get_pressed()
    
    # --- ESTADO: MENU INICIAL ---
    if game_state == "MENU":
        draw_menu() # Função que desenha a história e opções

    # --- ESTADO: CONFIGURAÇÕES ---
    elif game_state == "CONFIG":
        draw_config()

    # --- ESTADO: PAUSE ---
    elif game_state == "PAUSE":
        msg = big_font.render("PAUSADO", True, (255, 255, 0))
        screen.blit(msg, (250, 250))
        sub = font.render("Pressione [P] para voltar", True, (255, 255, 255))
        screen.blit(sub, (280, 330))

    # --- ESTADO: JOGANDO (Sua lógica original aqui) ---
    elif game_state == "PLAYING":
        # Controles Player
        if keys[pygame.K_LEFT] and player_X > 0: player_X -= player_speed
        if keys[pygame.K_RIGHT] and player_X < 736: player_X += player_speed
        if keys[pygame.K_SPACE] and bullet_state == "rest":
            bullet_X = player_X + 16
            bullet_Y = player_Y
            bullet_state = "fire"
            laser_sound.play()

        # Bala
        if bullet_state == "fire":
            screen.blit(bulletImage, (bullet_X, bullet_Y))
            bullet_Y -= bullet_speed
            if bullet_Y < 0: bullet_state = "rest"

        # Lógica dos Aliens
        for i in range(len(aliens) - 1, -1, -1):
            et = aliens[i]
            et["x"] += et["speed"]

            if et["x"] <= 0 or et["x"] >= 736:
                et["speed"] *= -1
                et["y"] += 40
            
            if et["y"] > 450:
                game_state = "GAMEOVER"
                break

            if bullet_state == "fire" and is_collision(et["x"], et["y"], bullet_X, bullet_Y):
                exp_X, exp_Y = et["x"], et["y"]
                exp_visible = True
                exp_timer = 15
                explosion_sound.play()
                aliens.pop(i) 
                bullet_state = "rest"
                score_val += 1
            else:
                screen.blit(et["img"], (et["x"], et["y"]))

        if len(aliens) == 0:
            if level_val < 4:
                level_val += 1
                game_state = "TRANSITION"
                transition_timer = 120 
            else:
                game_state = "WIN"

        screen.blit(playerImage, (player_X, player_Y))
        show_ui()

    # --- ESTADOS DE TRANSIÇÃO, VITÓRIA E DERROTA ---
    elif game_state == "TRANSITION":
        msg = big_font.render(f"LEVEL {level_val}", True, (255, 255, 0))
        screen.blit(msg, (250, 250))
        transition_timer -= 1
        if transition_timer <= 0:
            spawn_aliens(level_val)
            player_speed += 1
            game_state = "PLAYING"

    elif game_state == "GAMEOVER":
        msg = big_font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(msg, (200, 250))
        sub = font.render("Pressione [R] para tentar novamente", True, (255, 255, 255))
        screen.blit(sub, (220, 350))

    elif game_state == "WIN":
        msg = big_font.render("PARABÉNS!", True, (0, 255, 0))
        screen.blit(msg, (220, 250))
        sub = font.render("Pressione [R] para jogar novamente", True, (255, 255, 255))
        screen.blit(sub, (230, 350))

    # Explosão (Desenha por cima de quase tudo)
    if exp_visible:
        tamanho = 50 + (level_val * 45)
        img_exp = pygame.transform.scale(explosionImage, (tamanho, tamanho))
        offset = tamanho // 2
        screen.blit(img_exp, (exp_X - offset + 20, exp_Y - offset + 20))
        exp_timer -= 1
        if exp_timer <= 0: exp_visible = False
    
    pygame.display.update()
    clock.tick(60)