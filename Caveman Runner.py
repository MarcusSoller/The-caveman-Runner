import pygame
import random

# =========================================================
# 🟡 1. INITIALIZATION
# =========================================================
pygame.init()
pygame.font.init()
pygame.mixer.init()

pygame.mixer.music.load("halloffame.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

trexroar = pygame.mixer.Sound("dino.mp3")
manscream = pygame.mixer.Sound("manscream.mp3")
buttonsound = pygame.mixer.Sound("button.wav")
jumpsound = pygame.mixer.Sound("jump.wav")
slidesound = pygame.mixer.Sound("slide.wav")
rollingstone = pygame.mixer.Sound("rollingstone.mp3")
snakehist = pygame.mixer.Sound("snakehist.mp3")
birdsound = pygame.mixer.Sound("birdsound.mp3")
raptorsound = pygame.mixer.Sound("raptorsound.mp3")
deathsound = pygame.mixer.Sound("eating.mp3")

game_font = pygame.font.SysFont('Comic Sans MS', 30, bold=True)
countdown_font = pygame.font.SysFont('Comic Sans MS', 120, bold=True)

SCREEN_WIDTH, SCREEN_HEIGHT = 1400, 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Caveman Runner")
# --- ADD THESE TWO LINES ---
game_icon = pygame.image.load('cavemanicon.png') # You can use one of your snake frames!
pygame.display.set_icon(game_icon)
# ---------------------------
clock = pygame.time.Clock()

# =========================================================
# 🟢 2. LOAD ASSETS
# =========================================================
bg_surface = pygame.image.load('backtredmill+2.jpg').convert()
bg_surface = pygame.transform.scale(bg_surface, (1400, 700))
bg_x = 0
bg_speed = 5

deco_frames = [pygame.transform.scale(pygame.image.load(f'trex{i}.png').convert_alpha(), (500, 500)) for i in range(4)]
deco_index, deco_x, deco_target_x = 0, -400, -260


# Load the pause image and scale it to 50x50 to match your pause_button_rect
pause_img = pygame.image.load("pauseb.png").convert_alpha()
pause_img = pygame.transform.scale(pause_img, (50, 50))

play_img = pygame.image.load("startb.png").convert_alpha()
play_img = pygame.transform.scale(play_img, (50, 50))


kilometer = pygame.transform.scale(pygame.image.load('kilometer.png').convert_alpha(), (300, 80))
eat_raptor = pygame.transform.scale(pygame.image.load("eatbyraptor.png").convert_alpha(), (400, 400))
eat_bird = pygame.transform.scale(pygame.image.load("eatbybird.png").convert_alpha(), (400, 400))
eat_trex = pygame.transform.scale(pygame.image.load("eatbytrex.png").convert_alpha(), (400, 400))
eat_snake = pygame.transform.scale(pygame.image.load("eatbysnakes.png").convert_alpha(), (400, 400))
tittle = pygame.transform.scale(pygame.image.load("title.png").convert_alpha(), (1000, 500))

pause_button_rect = pygame.Rect(20, 20, 50, 50)
startb_img = pygame.transform.scale(pygame.image.load("startb.png").convert_alpha(), (100, 100))
restartb_img = pygame.transform.scale(pygame.image.load("restartb.png").convert_alpha(), (100, 100))
start_button_rect = startb_img.get_rect(center=(700, 350))
restart_button_rect = restartb_img.get_rect(center=(700, 600))

snake_frames = [pygame.image.load(f'snake{i}.png').convert_alpha() for i in range(6)]
raptor_frames = [pygame.image.load(f'raptors{i}.png').convert_alpha() for i in range(3)]
bird_frames = [pygame.image.load(f'bird{i}.png').convert_alpha() for i in range(6)]
stone_img = pygame.image.load('stone.png').convert_alpha()

walk_images = [pygame.transform.scale(pygame.image.load(f'caveman walk ({i}).png').convert_alpha(), (150, 150)) for i in
               range(6)]
prepare_images = [pygame.transform.scale(pygame.image.load(f'eye{i}.png').convert_alpha(), (150, 150)) for i in
                  range(16)]
run_images = [pygame.transform.scale(pygame.image.load(f'caveman run ({i}).png').convert_alpha(), (150, 150)) for i in
              range(6)]
duck_images = [pygame.transform.scale(pygame.image.load(f'slider ({i}).png').convert_alpha(), (160, 160)) for i in
               range(4)]

# =========================================================
# 🔵 3. VARIABLES
# =========================================================
gravity = 0.8
GROUND_Y = 425
dino_velocity = 0
is_jumping = False
is_ducking = False
game_active = False
waiting_to_start = True
is_counting_down = False
waiting_to_restart = False
is_paused = False
countdown_timer = 0
score = 0
obstacle_speed = 10
spawn_timer = 0
obstacles = []
last_hit_obstacle = None
walk_index = 0
dino_rect = pygame.Rect(350, GROUND_Y, 100, 100)

# =========================================================
# 🔴 4. MAIN LOOP
# =========================================================
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_active and pause_button_rect.collidepoint(event.pos):
                buttonsound.play()
                is_paused = not is_paused
                if is_paused:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()

            elif waiting_to_start and start_button_rect.collidepoint(event.pos):
                buttonsound.play()
                waiting_to_start = False
                is_counting_down = True
                countdown_timer = pygame.time.get_ticks()
                trexroar.play()  # Start the roar
                manscream.play()

            elif waiting_to_restart and restart_button_rect.collidepoint(event.pos):
                buttonsound.play()
                waiting_to_restart = False
                is_counting_down = True
                countdown_timer = pygame.time.get_ticks()
                is_paused = False
                game_active = False
                is_jumping = False
                is_ducking = False
                score = 0
                obstacles.clear()
                dino_rect.y = GROUND_Y
                spawn_timer = 0
                bg_x = 0
                pygame.mixer.music.play(-1)
                trexroar.play()  # Play sounds for restart too
                manscream.play()

        if event.type == pygame.KEYDOWN and not is_paused:
            if event.key == pygame.K_UP and not is_jumping and game_active:
                jumpsound.play()
                dino_velocity = -20
                is_jumping = True
            if event.key == pygame.K_DOWN and game_active:
                is_ducking = True
                slidesound.play()
                if is_jumping: dino_velocity = 15

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                is_ducking = False
                slidesound.stop()

    # --- LOGIC ---
    if not is_paused:
        if game_active:
            current_set = duck_images if is_ducking and not is_jumping else run_images
            anim_speed = 0.15 if is_ducking else 0.10
        elif is_counting_down:
            current_set = prepare_images
            anim_speed = 0.08
        else:
            current_set = walk_images
            anim_speed = 0.05

        walk_index = (walk_index + anim_speed) % len(current_set)
        deco_index = (deco_index + 0.1) % 4

        if is_counting_down:
            if deco_x < deco_target_x: deco_x += 5
            if pygame.time.get_ticks() - countdown_timer > 3000:
                is_counting_down = False
                game_active = True

        if game_active:
            dino_velocity += gravity
            dino_rect.y += dino_velocity
            score += 0.1
            obstacle_speed = 15 + (int(score) // 200)

            spawn_timer += 1
            if spawn_timer >= 150:
                obs_type = random.choice(['snake', 'stone', 'raptor', 'bird'])
                if obs_type == 'snake':
                    rect = pygame.Rect(1400, 440, 80, 110)
                    snakehist.play()
                elif obs_type == 'stone':
                    rect = pygame.Rect(1400, 470, 100, 100)
                    rollingstone.play()
                elif obs_type == 'raptor':
                    rect = pygame.Rect(1400, 410, 140, 140)
                    raptorsound.play()
                else:
                    rect = pygame.Rect(1400, 300, 200, 200)
                    birdsound.play()
                obstacles.append({'rect': rect, 'type': obs_type, 'anim_index': 0, 'angle': 0})
                spawn_timer = 0

            if dino_rect.y >= GROUND_Y:
                dino_rect.y = GROUND_Y
                dino_velocity = 0
                is_jumping = False

            collision_rect = pygame.Rect(dino_rect.x, GROUND_Y + 60, 100,
                                         40) if is_ducking and not is_jumping else dino_rect.inflate(-40, 0)

            for obs in obstacles:
                obs['rect'].x -= obstacle_speed
                if obs['type'] != 'stone':
                    obs['anim_index'] = (obs['anim_index'] + 0.15) % (3 if obs['type'] == 'raptor' else 6)
                else:
                    obs['angle'] -= obstacle_speed

                if collision_rect.colliderect(obs['rect'].inflate(0, -40)):
                    pygame.mixer.music.stop()
                    deathsound.play()
                    game_active, waiting_to_restart = False, True
                    last_hit_obstacle = obs['type']

            obstacles = [o for o in obstacles if o['rect'].x > -200]

    # --- DRAWING ---
    screen.blit(bg_surface, (bg_x, 0))
    screen.blit(bg_surface, (bg_x + 1400, 0))
    if game_active and not is_paused:
        bg_x -= bg_speed
        if bg_x <= -1400: bg_x = 0

    if game_active:
        for obs in obstacles:
            if obs['type'] == 'stone':
                img = pygame.transform.rotate(
                    pygame.transform.scale(stone_img, (obs['rect'].width, obs['rect'].height)), -obs['angle'])
                screen.blit(img, img.get_rect(center=obs['rect'].center).topleft)
            else:
                frames = snake_frames if obs['type'] == 'snake' else raptor_frames if obs[
                                                                                          'type'] == 'raptor' else bird_frames
                img = frames[int(obs['anim_index'])]
                screen.blit(pygame.transform.scale(img, (obs['rect'].width, obs['rect'].height)),
                            (obs['rect'].x, obs['rect'].y))

    draw_y = GROUND_Y - 25 if is_ducking and not is_jumping else dino_rect.y - 25
    screen.blit(current_set[int(walk_index)], (dino_rect.x - 25, draw_y))

    if is_counting_down or game_active:
        screen.blit(deco_frames[int(deco_index)], (deco_x, 100))

    if game_active or not waiting_to_start:
        screen.blit(kilometer, (1100, 35))
        score_surf = game_font.render(f'KM:{int(score)}', True, (0, 0, 0))
        screen.blit(score_surf, score_surf.get_rect(topright=(1300, 50)))

    if is_counting_down:
        val = str(3 - ((pygame.time.get_ticks() - countdown_timer) // 1000))
        txt = countdown_font.render(val, True, (255, 255, 0))
        screen.blit(txt, txt.get_rect(center=(700, 200)))

    if waiting_to_start:
        screen.blit(tittle, (190, 100))
        screen.blit(startb_img, start_button_rect)

    if waiting_to_restart:
        overlay = pygame.Surface((1400, 700), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        death_img = eat_snake if last_hit_obstacle == "snake" else eat_raptor if last_hit_obstacle == "raptor" else eat_bird if last_hit_obstacle == "bird" else eat_trex
        screen.blit(game_font.render('GAME OVER', True, (255, 0, 0)), (630, 450))
        screen.blit(pygame.transform.scale(death_img, (400, 400)), (505, 50))
        screen.blit(restartb_img, restart_button_rect)

    if game_active:
        if is_paused:
            # Show a Play icon if the game is currently paused
            screen.blit(play_img, (pause_button_rect.x, pause_button_rect.y))
        else:
            # Show the Pause icon while the game is running
            screen.blit(pause_img, (pause_button_rect.x, pause_button_rect.y))

    if is_paused:
        p_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        p_overlay.fill((0, 0, 0, 120))
        screen.blit(p_overlay, (0, 0))
        p_txt = countdown_font.render("PAUSED", True, (255, 255, 0))
        screen.blit(p_txt, p_txt.get_rect(center=(700, 350)))

    pygame.display.update()
    clock.tick(60)

pygame.quit()