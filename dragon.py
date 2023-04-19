
import os
import random
import sys
import time

import pygame

pygame.init()
# Initialization
display = pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h))
pygame.display.set_caption('The Dragon')
pygame.display.set_icon(pygame.transform.scale(pygame.image.load(f'assets{os.sep}icon.png'), (256, 256)))
screen = pygame.Surface(display.get_size())
alpha_screen = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
clock = pygame.time.Clock()
font = pygame.font.SysFont('Times New Roman', display.get_width() // 7)

THE = font.render('THE ', True, (255, 255, 0), (220, 120, 62))
DRAGON = font.render('DRAGON', True, (255, 0, 0), (220, 120, 62))
title_surf = pygame.Surface((THE.get_width() + DRAGON.get_width(), max(THE.get_height(), DRAGON.get_height())))
title_surf.fill((220, 120, 62))
title_surf.blit(THE, (0, 0))
title_surf.blit(DRAGON, (THE.get_width(), 0))
win_surf = font.render('You have slain', True, (62, 162, 220), (220, 120, 62))
lose_surf = font.render('You have died to', True, (102, 0, 0), (220, 120, 62))

PROJECTILEEVENT = pygame.event.custom_type()
WALLEVENT = pygame.event.custom_type()

FPS = 60
dt = 1.0
last_time = time.time()
movement = {'u': False, 'd': False, 'l': False, 'r': False}
moved = [0, 0]
g = 3/4
acc = 0
speed = 1
projectile_speed = 4
bullets = []
# Sounds
shoot_sound = pygame.mixer.Sound(f'assets{os.sep}shoot.wav')
shoot_sound.set_volume(0.5)
dragon_hurt_sound = pygame.mixer.Sound(f'assets{os.sep}dragon_hurt.wav')
player_hurt_sound = pygame.mixer.Sound(f'assets{os.sep}player_hurt.wav')
# Player values
gun_yellow = pygame.Surface((64, 16), pygame.SRCALPHA)
pygame.draw.rect(gun_yellow, (255, 255, 0), (0, 0, 64, 8))
pygame.draw.rect(gun_yellow, (255, 255, 0), (0, 0, 8, 16))
gun_red = pygame.Surface((64, 16), pygame.SRCALPHA)
pygame.draw.rect(gun_red, (255, 0, 0), (0, 0, 64, 8))
pygame.draw.rect(gun_red, (255, 0, 0), (0, 0, 8, 16))
player = pygame.Rect(10 + gun_red.get_width(), 3 * display.get_height() // 4 - 96, 54, 96)
player_hp = 1000
player_flip = False
last_shot_red = False
shoot_cooldown = FPS
# Dragon values
dragon = pygame.Rect(display.get_width() - 78, 3 * display.get_height() // 4 - 96, 54, 96)
dragon_hp = 1000
max_dragon_hp = 1000
dragon_timer = 5 * FPS // 2
attacks = {'projectile': PROJECTILEEVENT, 'wall': WALLEVENT}
projectiles = []
projectile_timer = 5 * FPS
walls = pygame.Rect(0, 0, 64, 3 * display.get_height() // 4), pygame.Rect(display.get_width() - 64, 0, 64, 3 * display.get_height() // 4)
right_wall_red = True
walls_active = [False, False]
wall_to_middle = True

screen_shake = 0
slomo = 0
slomo_cooldown = 10 * FPS

while True:
    # Fill screen and update ∆t
    screen.fill((220, 120, 62))
    dt = (time.time() - last_time) * FPS
    last_time = time.time()
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                movement['u'] = True
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                movement['d'] = True
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                movement['l'] = True
                player_flip = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                movement['r'] = True
                player_flip = False
            if event.key == pygame.K_SPACE:
                # Shooting
                if player_hp > 0:
                    if shoot_cooldown <= 0:
                        if not player_flip:
                            if last_shot_red:
                                bullets.append((pygame.Rect(player.right, player.y + 3 * player.h // 5, 16, 8), 'r-'))
                            else:
                                bullets.append((pygame.Rect(player.right, player.y + 3 * player.h // 5, 16, 8), 'y+'))
                            moved[0] -= 16
                        else:
                            if last_shot_red:
                                bullets.append((pygame.Rect(player.x, player.y + 3 * player.h // 5, 16, 8), 'r+'))
                            else:
                                bullets.append((pygame.Rect(player.x, player.y + 3 * player.h // 5, 16, 8), 'y-'))
                            moved[0] += 16
                        last_shot_red = not last_shot_red
                        screen_shake += FPS // 4
                        shoot_sound.play()
                        shoot_cooldown = FPS
            if event.key == pygame.K_e:
                if slomo_cooldown <= 0:
                    slomo = 5 * FPS
                    slomo_cooldown = 15 * FPS
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                movement['u'] = False
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                movement['d'] = False
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                movement['l'] = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                movement['r'] = False
        if event.type == PROJECTILEEVENT:
            projectile_timer = 6 * FPS
            if dragon_hp > 0:
                for i in range(3):
                    projectiles.append([pygame.Rect(dragon.x + dragon.w // 2 - 16, dragon.y + dragon.h // 2 - 16, 32, 32), 'r', False])
                    projectiles.append([pygame.Rect(dragon.x + dragon.w // 2 - 16, dragon.y + dragon.h // 2 - 16, 32, 32), 'y', False])
        if event.type == WALLEVENT:
            right_wall_red = not right_wall_red
            if dragon_hp > 0:
                walls_active = [True, True]
                wall_to_middle = True
            walls = pygame.Rect(0, 0, 64, 3 * display.get_height() // 4), pygame.Rect(display.get_width() - 64, 0, 64, 3 * display.get_height() // 4)

    alpha_screen.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_MULT)
    # Movement
    player.y += acc * speed
    acc += g * speed

    if movement['u']:
        moved[1] -= 24 * speed * dt
    if movement['d']:
        moved[1] += 16 * speed * dt
    if movement['l']:
        moved[0] -= 16 * speed * dt
    if movement['r']:
        moved[0] += 16 * speed * dt
    player.y += moved[1]
    player.x += moved[0]
    if player.right > display.get_width():
        player.right = display.get_width()
    if player.x < 0:
        player.x = 0
    if player.bottom > 3 * display.get_height() // 4:
        player.bottom = 3 * display.get_height() // 4
        acc = 0
    if player.y < 0:
        player.y = 0
    moved = [0, 0]

    if player.colliderect(dragon):
        if dragon_hp > 0 and player_hp > 0:
            player_hp -= 20
            player_hurt_sound.play()
    # Handle timersd
    if screen_shake > 0:
        screen_shake -= speed
    if slomo_cooldown > 0:
        slomo_cooldown -= speed
    if shoot_cooldown > 0:
        shoot_cooldown -= speed
    if projectile_timer > 0:
        projectile_timer -= 1
    if slomo > 0:
        slomo -= 1
        speed = 0.5
    else:
        speed = 1
    if dragon_timer > 0:
        dragon_timer -= speed
    else:
        dragon_timer = 5 * FPS
        if dragon_hp > 0:
            dragon.x, dragon.y = random.randint(0, display.get_width() - dragon.w), random.randint(0, 3 * display.get_height() // 4 - dragon.h)
            while dragon.colliderect(player):
                dragon.x, dragon.y = random.randint(0, display.get_width() - dragon.w), random.randint(0, 3 * display.get_height() // 4 - dragon.h)
            pygame.event.post(pygame.event.Event(random.choice(tuple(attacks.values())), {}))
    # Handle fire walls
    if walls[0].colliderect(player) and walls_active[0] and player_hp > 0:
        walls_active[0] = False
        player_hp -= 100
        player_hurt_sound.play()
    if walls[1].colliderect(player) and walls_active[1] and player_hp > 0:
        walls_active[1] = False
        player_hp -= 100
        player_hurt_sound.play()
    if wall_to_middle:
        if walls_active[0]:
            walls[0].x += 10
        if walls_active[1]:
            walls[1].x -= 10
    else:
        if walls_active[0]:
            walls[0].x -= 8
        if walls_active[1]:
            walls[1].x += 8
    if walls[0].right > display.get_width() // 2 - 77:
        wall_to_middle = False
    if walls[1].x < display.get_width() // 2 + 77:
        wall_to_middle = False
    if walls[0].x <= 0:
        walls_active = [False, False]
    if walls[1].right >= display.get_width():
        walls_active = [False, False]
    # Handle bullets
    for bullet in bullets:
        if bullet[1][1] == '+':
            bullet[0].x += 32 * speed * dt
        elif bullet[1][1] == '-':
            bullet[0].x -= 32 * speed * dt
        if bullet[0].colliderect(dragon):
            dragon_hp -= 100
            if dragon_hp > 0:
                bullets.remove(bullet)
                dragon_hurt_sound.play()
        if bullet[0].x > display.get_width() or bullet[0].right < 0:
            bullets.remove(bullet)
        if bullet[0].colliderect(walls[0]):
            if right_wall_red and bullet[1][0] == 'y':
                walls_active[0] = False
            elif not right_wall_red and bullet[1][0] == 'r':
                walls_active[0] = False
        if bullet[0].colliderect(walls[1]):
            if not right_wall_red and bullet[1][0] == 'y':
                walls_active[1] = False
            elif right_wall_red and bullet[1][0] == 'r':
                walls_active[1] = False
    # Handle dragon projectiles
    if not projectile_timer % 5:
        for projectile in projectiles:
            if not projectile[2]:
                projectile[2] = True
                break

    for projectile in projectiles:
        if projectile[2] and player_hp > 0:
            moving = [projectile_speed * dt if projectile[0].x < player.x + player.w // 2 else -projectile_speed * dt, projectile_speed * dt if projectile[0].y < player.y + player.h // 2 else -projectile_speed * dt]
            projectile[0].x += moving[0]
            projectile[0].y += moving[1]
        if projectile[0].bottom > 3 * display.get_height() // 4 or projectile[0].x < 0 or projectile[0].x > display.get_width():
            projectiles.remove(projectile)
        if projectile[0].colliderect(player) and player_hp > 0:
            player_hp -= 50
            player_hurt_sound.play()
            projectiles.remove(projectile)
        collides = projectile[0].collidelist([pygame.Rect(bullet[0].x, bullet[0].y, bullet[0].w + 32, bullet[0].h) for bullet in bullets if bullet[1][0] == projectile[1]])
        if collides > -1:
            projectiles.remove(projectile)
        if projectile[0].colliderect(dragon) and dragon_hp > 0 and dragon_timer < 2 * FPS and player_hp > 0:
            dragon_hp -= 40
            dragon_hurt_sound.play()
            projectiles.remove(projectile)
    # Rendering to the display
    if screen_shake > 0:
        screen.blit(title_surf, (display.get_width() // 2 - title_surf.get_width() // 2 + random.randint(-24, 24), display.get_height() // 2 - title_surf.get_height() // 2 + random.randint(-24, 24)))
        if dragon_hp <= 0:
            screen.blit(win_surf, (display.get_width() // 2 - win_surf.get_width() // 2, display.get_height() // 2 - win_surf.get_height() // 2 - title_surf.get_height()))
        elif player_hp <= 0:
            screen.blit(lose_surf, (display.get_width() // 2 - lose_surf.get_width() // 2 + random.randint(-24, 24), display.get_height() // 2 - lose_surf.get_height() // 2 - title_surf.get_height() + random.randint(-24, 24)))
    else:
        screen.blit(title_surf, (display.get_width() // 2 - title_surf.get_width() // 2 + random.randint(-1, 1), display.get_height() // 2 - title_surf.get_height() // 2 + random.randint(-1, 1)))
        if dragon_hp <= 0:
            screen.blit(win_surf, (display.get_width() // 2 - win_surf.get_width() // 2 + random.randint(-1, 1), display.get_height() // 2 - win_surf.get_height() // 2 - title_surf.get_height() + random.randint(-1, 1)))
        elif player_hp <= 0:
            screen.blit(lose_surf, (display.get_width() // 2 - lose_surf.get_width() // 2 + random.randint(-1, 1), display.get_height() // 2 - lose_surf.get_height() // 2 - title_surf.get_height() + random.randint(-1, 1)))
    pygame.draw.rect(alpha_screen, (196, 94, 35), (0, 3 * display.get_height() // 4, display.get_width(), display.get_height() // 4))
    if player_hp > 0:
        pygame.draw.rect(alpha_screen, (62 * player_hp // 1000, 220 * player_hp // 1000, 120 * player_hp // 1000), player)
    for bullet in bullets:
        if bullet[1][0] == 'r':
            pygame.draw.rect(alpha_screen, (255, 0, 0), bullet[0])
        elif bullet[1][0] == 'y':
            pygame.draw.rect(alpha_screen, (255, 255, 0), bullet[0])
    if player_hp > 0:
        if not player_flip:
            alpha_screen.blit(pygame.transform.flip(gun_red, True, False), (player.x + player.w // 10 - gun_red.get_width(), player.y + 3 * player.h // 5))
            alpha_screen.blit(gun_yellow, (player.x + 9 * player.w // 10, player.y + 3 * player.h // 5))
        else:
            alpha_screen.blit(gun_red, (player.x + 9 * player.w // 10, player.y + 3 * player.h // 5))
            alpha_screen.blit(pygame.transform.flip(gun_yellow, True, False), (player.x + player.w // 10 - gun_yellow.get_width(), player.y + 3 * player.h // 5))
    if dragon_hp > 0:
        pygame.draw.rect(alpha_screen, (220 * dragon_hp // max_dragon_hp, 62 * dragon_hp // max_dragon_hp, 83 * dragon_hp // max_dragon_hp), dragon)
    for projectile in projectiles:
        if projectile[1] == 'r':
            pygame.draw.rect(alpha_screen, (255, 0, 0), projectile[0])
        elif projectile[1] == 'y':
            pygame.draw.rect(alpha_screen, (255, 255, 0), projectile[0])
    if walls_active[0]:
        if right_wall_red:
            pygame.draw.rect(alpha_screen, (255, 255, 0), walls[0])
        else:
            pygame.draw.rect(alpha_screen, (255, 0, 0), walls[0])
    if walls_active[1]:
        if right_wall_red:
            pygame.draw.rect(alpha_screen, (255, 0, 0), walls[1])
        else:
            pygame.draw.rect(alpha_screen, (255, 255, 0), walls[1])
    if screen_shake > 0:
        screen.blit(alpha_screen, (random.randint(-24, 24) * speed, random.randint(-24, 24) * speed))
    else:
        screen.blit(alpha_screen, (random.randint(-1, 1), random.randint(-1, 1)))
    display.blit(screen, (0, 0))
    pygame.display.flip()
    clock.tick(FPS)
