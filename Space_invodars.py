import math
import random
import pygame
from pygame import mixer

# Inicialização
pygame.init()
mixer.init()

# ÁUDIO
mixer.music.load("data/sounds/Intro.wav")
mixer.music.set_volume(0.05)
mixer.music.play(-1)

explosion_sound = mixer.Sound('data/sounds/explosion.wav')
explosion_sound.set_volume(0.1)

laser_sound = mixer.Sound('data/sounds/bullet.wav')
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

explosionImage = load_img('data/Sprites/explosion.png')
specialBulletImage = load_img('data/Sprites/bullet_5.png', (250,250)) 

bg_images = [
    load_img('data/backgrounds/BG_1.jpg', (800, 600)),
    load_img('data/backgrounds/BG_2.png', (800, 600)),
    load_img('data/backgrounds/BG_3.png', (800, 600)),
    load_img('data/backgrounds/BG_4.png', (800, 600))
]

font = pygame.font.Font('freesansbold.ttf', 20)
big_font = pygame.font.Font('freesansbold.ttf', 64)

# Variáveis de Estado
level_val = 1
score_total = 0 # Pontuação total do jogo
kills_count = 0 # Contador para o especial 
special_available = False
special_state = "rest"
special_X, special_Y = 0, 0
special_speed = 15
is_special_hit = False

game_state = "MENU" 
music_muted = False
effects_muted = False

player_X = 370
player_Y = 523
player_speed = 5

bullet_X, bullet_Y = 0, 523
bullet_state = "rest"
bullet_speed = 12

exp_X, exp_Y = 0, 0
exp_visible = False
exp_timer = 0

bullet_speeds = {
    1: 7,  
    2: 9,  
    3: 10,  
    4: 15, 
    "special": 7
}

aliens = [] 

def spawn_aliens(level):
    aliens.clear()
    qtd = 8 + (level * 6) 
    speed = 0.8 + (level * 0.5)
    img_path = f'data/Sprites/alien_{min(level, 4)}.png'
    for i in range(qtd):
        aliens.append({
            "x": random.randint(64, 730),
            "y": random.randint(30, 150),
            "speed": speed if random.random() > 0.5 else -speed,
            "img": load_img(img_path)
        })

def update_assets():
    """Atualiza as sprites de nave e bala de acordo com o nível atual."""
    global playerImage, bulletImage, specialBulletImage

    if level_val == 4:
        playerImage = load_img('data/Sprites/nave_2.png', (100, 150))
    else:
        playerImage = load_img('data/Sprites/nave1.png')

    b_suffix = f"_{level_val}" if level_val > 1 else ""
    bulletImage = load_img(f'data/Sprites/bullet{b_suffix}.png')

    specialBulletImage = load_img('data/Sprites/bullet_5.png', (100, 100))
    
spawn_aliens(1)
update_assets()

def show_ui():
    score_text = font.render(f"Score: {score_total} | ETs: {len(aliens)}", True, (255, 255, 255))
    level_text = font.render(f"Level: {level_val}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 35))

    if special_available:
        spec_text = font.render("ESPECIAL PRONTO [E]!", True, (255, 215, 0))
        screen.blit(spec_text, (screen_width - 250, 10))
    else:
        prog_text = font.render(f"Especial: {kills_count}/25", True, (200, 200, 200))
        screen.blit(prog_text, (screen_width - 180, 10))

def is_collision(x1, y1, x2, y2, ox=32, oy=32):
    distance = math.sqrt(((x1 + ox) - x2)**2 + ((y1 + oy) - y2)**2)
    return distance < 50 


def draw_text_centered(text, font, color, y_offset):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(screen_width // 2, y_offset))
    screen.blit(render, rect)

def draw_menu():
    screen.blit(bg_images[0], (0, 0))
    small_f = pygame.font.Font('freesansbold.ttf', 16)
    draw_text_centered("A galaxia ânima foi atacada por uma raça chamada invodars,", small_f, (255, 255, 255), 150)
    draw_text_centered("você é o único que pode parar esta invasão!", small_f, (255, 255, 255), 175)
    draw_text_centered("Mova-se com as SETAS, atire com ESPAÇO e use ESPECIAL com [E]", small_f, (255, 255, 255), 220)
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


running = True
while running:
    # 1. Background
    if game_state in ["MENU", "CONFIG"]:
        screen.blit(bg_images[0], (0, 0))
    else:
        screen.blit(bg_images[min(level_val-1, 3)], (0, 0))
    
    # 2. SISTEMA DE EVENTOS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_state == "MENU":
                if event.key == pygame.K_RETURN: game_state = "PLAYING"
                if event.key == pygame.K_c: game_state = "CONFIG"
            elif game_state == "CONFIG":
                if event.key == pygame.K_1:
                    music_muted = not music_muted
                    mixer.music.set_volume(0 if music_muted else 0.05)
                if event.key == pygame.K_2:
                    effects_muted = not effects_muted
                    explosion_sound.set_volume(0 if effects_muted else 0.1)
                    laser_sound.set_volume(0 if effects_muted else 0.015)
                if event.key == pygame.K_ESCAPE: game_state = "MENU"
            elif game_state == "PLAYING":
                if event.key == pygame.K_p: game_state = "PAUSE"
                # Input do Especial
                if event.key == pygame.K_e and special_available and special_state == "rest":
                    # Centraliza o tiro de 100px na nave de 100px
                    special_X = player_X - 3
                    special_Y = player_Y - 50
                    special_state = "fire"
                    special_available = False
                    kills_count = 0
                    laser_sound.play()
            elif game_state == "PAUSE":
                if event.key == pygame.K_p: game_state = "PLAYING"
            elif game_state in ["WIN", "GAMEOVER"]:
                if event.key == pygame.K_r:
                    score_total = 0
                    kills_count = 0
                    level_val = 1
                    special_available = False
                    spawn_aliens(1)
                    update_assets()
                    game_state = "PLAYING"

    keys = pygame.key.get_pressed()
    
    if game_state == "MENU":
        draw_menu()
    elif game_state == "CONFIG":
        draw_config()
    elif game_state == "PAUSE":
        draw_text_centered("PAUSADO", big_font, (255, 255, 0), 250)
        draw_text_centered("Pressione [P] para voltar", font, (255, 255, 255), 330)

    elif game_state == "PLAYING":
        render_y = player_Y - 80 if level_val == 4 else player_Y
        # Controles
        if keys[pygame.K_LEFT] and player_X > 0: player_X -= player_speed
        if keys[pygame.K_RIGHT] and player_X < 736: player_X += player_speed
        if keys[pygame.K_SPACE] and bullet_state == "rest":
            if level_val == 1:
                bullet_offset = 26
            elif level_val == 2:
                bullet_offset = 31
            elif level_val == 3:
                bullet_offset = 10
            elif level_val == 4:
                bullet_offset = 10 
            else:
                bullet_offset = 10

            bullet_X = player_X + bullet_offset
            bullet_Y = render_y 
            bullet_state = "fire"
            laser_sound.play()

        # Especial Disponível?
        if kills_count >= 25:
            special_available = True

        # Movimentação das Balas
        if bullet_state == "fire":
            screen.blit(bulletImage, (bullet_X, bullet_Y))
            
            # Velocidade dinâmica por level
            if level_val == 2:
                bullet_Y -= 14 
            else:
                bullet_Y -= bullet_speed
                
            if bullet_Y < 0: bullet_state = "rest"
        
        if special_state == "fire":
            screen.blit(specialBulletImage, (special_X, special_Y))
            special_Y -= special_speed
            if special_Y < 0: special_state = "rest"

        for i in range(len(aliens) - 1, -1, -1):
            et = aliens[i]
            et["x"] += et["speed"]

            if et["x"] <= 0 or et["x"] >= 736:
                et["speed"] *= -1
                et["y"] += 40
            
            limit_y = 400 if level_val == 4 else 430
            if et["y"] > limit_y:
                game_state = "GAMEOVER"
                break

            if level_val == 1:
                off_x = 16 
                off_y = 25 
            if level_val == 2:
                off_x = 52  
                off_y = 51  
            if level_val == 3:
                off_x = 30  
                off_y = 30  
            if level_val == 4:
                off_x = 56  
                off_y = 35  

            # Colisão Especial
            if special_state == "fire" and is_collision(et["x"], et["y"], special_X, special_Y, off_x, off_y):
                exp_X, exp_Y = et["x"], et["y"]
                exp_visible, exp_timer = True, 25
                is_special_hit = True
                explosion_sound.play()
                aliens.pop(i)
                special_state = "rest"
                score_total += 1
            # Colisão Normal
            elif bullet_state == "fire" and is_collision(et["x"], et["y"], bullet_X, bullet_Y, off_x, off_y):
                exp_X, exp_Y = et["x"], et["y"]
                exp_visible, exp_timer = True, 15
                is_special_hit = False
                explosion_sound.play()
                aliens.pop(i) 
                bullet_state = "rest"
                score_total += 1
                kills_count += 1
            else:
                screen.blit(et["img"], (et["x"], et["y"]))

        # Mapeamento rápido de velocidades
        bullet_speed_map = {1: 10, 2: 13, 3: 16, 4: 20}
        bullet_speed = bullet_speed_map.get(level_val, 12)
        special_speed = 7 

        if len(aliens) == 0:
            if level_val < 4:
                level_val += 1
                update_assets() # Troca nave/balas
                game_state = "TRANSITION"
                transition_timer = 120 
            else:
                game_state = "WIN"

        render_y = player_Y - 80 if level_val == 4 else player_Y
        screen.blit(playerImage, (player_X, render_y))
        show_ui()

    elif game_state == "TRANSITION":
        draw_text_centered(f"LEVEL {level_val}", big_font, (255, 255, 0), 250)
        transition_timer -= 1
        if transition_timer <= 0:
            spawn_aliens(level_val)
            player_speed += 1
            game_state = "PLAYING"

    elif game_state == "GAMEOVER":
        draw_text_centered("GAME OVER", big_font, (255, 0, 0), 250)
        draw_text_centered("Pressione [R] para tentar novamente", font, (255, 255, 255), 350)

    elif game_state == "WIN":
        draw_text_centered("PARABÉNS!", big_font, (0, 255, 0), 250)
        draw_text_centered("Pressione [R] para jogar novamente", font, (255, 255, 255), 350)

    # Explosão
    if exp_visible:
        mult = 3 if is_special_hit else 1
        tamanho = (40 + (level_val * 45)) * mult
        img_exp = pygame.transform.scale(explosionImage, (tamanho, tamanho))
        offset = tamanho // 2
        screen.blit(img_exp, (exp_X - offset + 20, exp_Y - offset + 20))
        exp_timer -= 1
        if exp_timer <= 0: exp_visible = False
    
    pygame.display.update()
    clock.tick(60)