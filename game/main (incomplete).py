import pygame
from pygame import mixer
import os
import random
import pickle

import button

pygame.init()
mixer.init()


def window():
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Shooter')

    # set framerate
    clock = pygame.time.Clock()
    FPS = 60

    return SCREEN_WIDTH, SCREEN_HEIGHT, screen, clock, FPS


def game_variables(SCREEN_HEIGHT):
    # define game variables
    GRAVITY = 0.75
    SCROLL_THRESH = 200
    ROWS = 16
    COLS = 150
    TILE_SIZE = SCREEN_HEIGHT // ROWS
    TILE_TYPES = len(os.listdir('images/tiles'))
    MAX_LEVELS = len(os.listdir('levels'))
    screen_scroll = 0
    background_scroll = 0
    level = 1
    start_game = False
    start_intro = False

    return GRAVITY, SCROLL_THRESH, ROWS, COLS, TILE_SIZE, TILE_TYPES, MAX_LEVELS, screen_scroll, background_scroll, level, start_game, start_intro


def player_action_variables():
    # define player action variables
    moving_left = False
    moving_right = False
    shoot = False
    grenade = False
    grenade_thrown = False

    return moving_left, moving_right, shoot, grenade, grenade_thrown


def audio():
    # load music and sounds
    pygame.mixer.music.load('audio/music2.mp3')
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1, 0.0, 5000)
    jump_fx = pygame.mixer.Sound('audio/jump.wav')
    jump_fx.set_volume(0.5)
    shot_fx = pygame.mixer.Sound('audio/shot.wav')
    shot_fx.set_volume(0.5)
    grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
    grenade_fx.set_volume(0.5)


def images():
    # button images
    start_img = pygame.image.load('images/buttons/start_button.png').convert_alpha()
    exit_img = pygame.image.load('images/buttons/exit_button.png').convert_alpha()
    restart_img = pygame.image.load('images/buttons/restart_button.png').convert_alpha()

    # background images
    pine1_img = pygame.image.load('images/background/pine1.png').convert_alpha()
    pine2_img = pygame.image.load('images/background/pine2.png').convert_alpha()
    mountain_img = pygame.image.load('images/background/mountain.png').convert_alpha()
    sky_img = pygame.image.load('images/background/sky_cloud.png').convert_alpha()

    pine1_img = pygame.transform.scale(pine1_img, (int(pine1_img.get_width() * 1.5), int(pine1_img.get_height() * 1.5)))
    pine2_img = pygame.transform.scale(pine2_img, (int(pine2_img.get_width() * 1.5), int(pine2_img.get_height() * 1.5)))
    mountain_img = pygame.transform.scale(mountain_img,
                                          (int(mountain_img.get_width() * 1.5), int(mountain_img.get_height() * 1.5)))
    sky_img = pygame.transform.scale(sky_img, (int(sky_img.get_width() * 1.5), int(sky_img.get_height() * 1.5)))

    # bullet
    bullet_img = pygame.image.load('images/icons/bullet.png').convert_alpha()
    # grenade
    grenade_img = pygame.image.load('images/icons/grenade.png').convert_alpha()
    # pick up boxes
    health_box_img = pygame.image.load('images/icons/health_box.png').convert_alpha()
    ammo_box_img = pygame.image.load('images/icons/ammo_box.png').convert_alpha()
    grenade_box_img = pygame.image.load('images/icons/grenade_box.png').convert_alpha()
    item_boxes = {
        'Health': health_box_img,
        'Ammo': ammo_box_img,
        'Grenade': grenade_box_img
    }

    return start_img, exit_img, restart_img, pine1_img, pine2_img, mountain_img, sky_img, pine1_img, pine2_img, mountain_img, sky_img, bullet_img, grenade_img, health_box_img, ammo_box_img, grenade_box_img, item_boxes


def store_tiles(TILE_SIZE, TILE_TYPES):
    # store tiles in a list
    img_list = []
    for current_tile in range(TILE_TYPES):
        img = pygame.image.load(f'images/tiles/{current_tile}.png')
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        img_list.append(img)


def colours_and_font():
    # define colours
    BACKGROUND = (144, 201, 120)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    PINK = (235, 65, 54)

    # define font
    font = pygame.font.SysFont('Futura', 30)

    return BACKGROUND, BLACK, WHITE, RED, GREEN, PINK, font


def draw_text(text, font, text_colour, x, y):
    img = font.render(text, True, text_colour)
    screen.blit(img, (x, y))


def draw_background():
    screen.fill(BACKGROUND)
    width = pine2_img.get_width()
    for repeat in range(5):  # how many times background repeats
        screen.blit(sky_img, ((repeat * width) - background_scroll * 0.5, 0))
        screen.blit(mountain_img,
                    ((repeat * width) - background_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 280))
        screen.blit(pine1_img,
                    ((repeat * width) - background_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((repeat * width) - background_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height() - 0))


# function to reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    damage_group.empty()
    next_group.empty()

    # create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'images/{self.char_type}/{animation}'))
            for frame_index in range(num_of_frames):
                img = pygame.image.load(f'images/{self.char_type}/{animation}/{frame_index}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump and not self.in_air:
            self.vel_y = -14
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # check for collision
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # if the ai has hit the wall then make it turn around
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if below the block, e.g. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the block, e.g. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # check for collision with damage blocks
        if pygame.sprite.spritecollide(self, damage_group, False):
            self.health = 0

        # check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, next_group, False):
            level_complete = True

        # check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # update scroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and background_scroll < (
                    world.level_length * TILE_SIZE) - SCREEN_WIDTH) \
                    or (self.rect.left < SCROLL_THRESH and background_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self, shot_fx):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery,
                            self.direction)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1
            shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            if not self.idling and random.randint(1, 200) == 1:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50
            # check if the ai is near the player
            if self.vision.colliderect(player.rect):
                # stop running and face the player
                self.update_action(0)  # 0: idle
                # shoot the player
                self.shoot()
            else:
                if not self.idling:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run
                    self.move_counter += 1
                    # update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction,
                                          self.rect.centery)  # 75 is half of vision so enemy sees full rectangle ahead
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        # scroll
        self.rect.x += screen_scroll

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)  # 3: death

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World:
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if 0 <= tile <= 10:  # dirt blocks
                        self.obstacle_list.append(tile_data)
                    elif 11 <= tile <= 13:  # decoration blocks
                        decoration = Decoration(img=img, x=(x * TILE_SIZE), y=(y * TILE_SIZE))
                        decoration_group.add(decoration)
                    elif 14 <= tile <= 16:  # damage blocks
                        damage = Damage(img=img, x=(x * TILE_SIZE), y=(y * TILE_SIZE))
                        damage_group.add(damage)
                    elif tile == 17:  # create health box
                        health_box = ItemBox(item_type='Health', x=(x * TILE_SIZE), y=(y * TILE_SIZE))
                        item_box_group.add(health_box)
                    elif tile == 18:  # create ammo box
                        ammo_box = ItemBox(item_type='Ammo', x=(x * TILE_SIZE), y=(y * TILE_SIZE))
                        item_box_group.add(ammo_box)
                    elif tile == 19:  # create grenade box
                        grenade_box = ItemBox(item_type='Grenade', x=(x * TILE_SIZE), y=(y * TILE_SIZE))
                        item_box_group.add(grenade_box)
                    elif tile == 20:  # create player
                        player = Soldier(char_type='player', x=(x * TILE_SIZE), y=(y * TILE_SIZE), scale=1.5, speed=5,
                                         ammo=20, grenades=5)
                        health_bar = HealthBar(x=10, y=10, health=player.health, max_health=player.max_health)
                    elif tile == 21:  # create enemies
                        enemy = Soldier(char_type='enemy', x=(x * TILE_SIZE), y=(y * TILE_SIZE), scale=1.5, speed=2,
                                        ammo=20, grenades=0)
                        enemy_group.add(enemy)
                    elif tile == 22:  # create exit
                        next = Next(img=img, x=(x * TILE_SIZE), y=(y * TILE_SIZE))
                        next_group.add(next)

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + TILE_SIZE - self.image.get_height())

    def update(self):
        self.rect.x += screen_scroll


class Damage(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + TILE_SIZE - self.image.get_height())

    def update(self):
        self.rect.x += screen_scroll


class Next(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + TILE_SIZE - self.image.get_height())

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # scroll
        self.rect.x += screen_scroll
        # check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            # check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            # delete the item box
            self.kill()


class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update with new health
        self.health = health
        # calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # check if bullet has gone off-screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # check collision with level (blocks)
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self, grenade_fx):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # check collision with level
        for tile in world.obstacle_list:
            # check collision with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # check if below the block, e.g. thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the block, e.g. thrown down
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        # update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy + screen_scroll

        # countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 2)
            explosion_group.add(explosion)
            # do damage to anyone that is nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 1 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 1:
                player.health -= 80
            elif abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            elif abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 3 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 3:
                player.health -= 20

            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 1 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 1:
                    enemy.health -= 100
                elif abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 75
                elif abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 3 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 3:
                    enemy.health -= 30


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        num_of_frames = len(os.listdir(f'images/explosion'))
        for frame in range(num_of_frames):
            img = pygame.image.load(f'images/explosion/{frame}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # scroll
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4
        # update explosion animation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class ScreenFade:
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:  # 1: whole screen fade outwards
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:  # 2: vertical screen fade down
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete


def screen_fades():
    # create screen fades
    intro_fade = ScreenFade(direction=1, colour=BLACK, speed=4)
    death_fade = ScreenFade(direction=2, colour=PINK, speed=5)

    return intro_fade, death_fade


def buttons():
    # create buttons
    start_button = button.Button(x=(SCREEN_WIDTH // 2 - 100), y=(SCREEN_HEIGHT // 2 - 150), image=start_img, scale=3)
    exit_button = button.Button(x=(SCREEN_WIDTH // 2 - 88), y=(SCREEN_HEIGHT // 2 + 10), image=exit_img, scale=3)
    restart_button = button.Button(x=(SCREEN_WIDTH // 2 - 115), y=(SCREEN_HEIGHT // 2 - 50), image=restart_img, scale=3)
    return start_button, exit_button, restart_button


def sprite_groups():
    # create sprite groups
    enemy_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    grenade_group = pygame.sprite.Group()
    explosion_group = pygame.sprite.Group()
    item_box_group = pygame.sprite.Group()
    decoration_group = pygame.sprite.Group()
    damage_group = pygame.sprite.Group()
    next_group = pygame.sprite.Group()
    return enemy_group, bullet_group, grenade_group, explosion_group, item_box_group, decoration_group, damage_group, next_group


def empty_tile_list():
    # create empty tile list
    world_data = []
    for row in range(ROWS):
        r = [-1] * COLS
        world_data.append(r)
    # load in level data and create world
    pickle_in = open(f'levels/{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
    world = World()
    player, health_bar = world.process_data(data=world_data)

    return world, player, health_bar


def game():
    run = True
    while run:

        clock.tick(FPS)

        if not start_game:
            # main menu
            screen.fill(BACKGROUND)
            # add buttons
            if start_button.draw(screen):
                start_game = True
                start_intro = True
            if exit_button.draw(screen):
                run = False
        else:
            # update background
            draw_background()
            # draw world map
            world.draw()
            # show player health
            health_bar.draw(player.health)
            # show ammo
            draw_text(f'AMMO: {player.ammo}', font, WHITE, 10, 35)
            for each_ammo in range(player.ammo):
                screen.blit(bullet_img, (120 + (each_ammo * 10), 40))
            # show grenades
            draw_text(f'GRENADES: {player.grenades}', font, WHITE, 10, 60)
            for each_grenade in range(player.grenades):
                screen.blit(grenade_img, (150 + (each_grenade * 20), 60))

            player.update()
            player.draw()

            for enemy in enemy_group:
                enemy.ai()
                enemy.update()
                enemy.draw()

            # update and draw groups
            bullet_group.update()
            grenade_group.update()
            explosion_group.update()
            item_box_group.update()
            decoration_group.update()
            damage_group.update()
            next_group.update()

            bullet_group.draw(screen)
            grenade_group.draw(screen)
            explosion_group.draw(screen)
            item_box_group.draw(screen)
            decoration_group.draw(screen)
            damage_group.draw(screen)
            next_group.draw(screen)

            # show intro
            if start_intro:
                if intro_fade.fade():
                    start_intro = False
                    intro_fade.fade_counter = 0

            # update player actions
            if player.alive:
                # shoot bullets
                if shoot:
                    player.shoot()
                # throw grenades
                elif grenade and not grenade_thrown and player.grenades > 0:
                    grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
                                      player.rect.top, player.direction)
                    grenade_group.add(grenade)
                    # reduce grenades
                    player.grenades -= 1
                    grenade_thrown = True
                if player.in_air:
                    player.update_action(2)  # 2: jump
                elif moving_left or moving_right:
                    player.update_action(1)  # 1: run
                else:
                    player.update_action(0)  # 0: idle
                screen_scroll, level_complete = player.move(moving_left, moving_right)
                background_scroll -= screen_scroll
                # check if player has completed the level
                if level_complete:
                    start_intro = True
                    level += 1
                    background_scroll = 0
                    world_data = reset_level()
                    if level <= MAX_LEVELS:
                        # load in level data and create world
                        pickle_in = open(f'levels/{level}_data', 'rb')
                        world_data = pickle.load(pickle_in)
                        world = World()
                        player, health_bar = world.process_data(data=world_data)

            else:
                screen_scroll = 0
                if death_fade.fade():
                    if restart_button.draw(screen):
                        death_fade.fade_counter = 0
                        start_intro = True
                        background_scroll = 0
                        world_data = reset_level()
                        # load in level data and create world
                        pickle_in = open(f'levels/{level}_data', 'rb')
                        world_data = pickle.load(pickle_in)
                        world = World()
                        player, health_bar = world.process_data(data=world_data)

        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                run = False
            # keyboard presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_q:
                    grenade = True
                if event.key == pygame.K_w and player.alive:
                    player.jump = True
                    jump_fx.play()
                if event.key == pygame.K_ESCAPE:
                    run = False
            # mouse clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:  # [0]: left mouse button
                    shoot = True

            # keyboard releases
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False
                if event.key == pygame.K_q:
                    grenade = False
                    grenade_thrown = False
            # mouse released
            if event.type == pygame.MOUSEBUTTONUP:
                shoot = False

        pygame.display.update()

pygame.quit()


if __name__ == "__main__":
    SCREEN_WIDTH, SCREEN_HEIGHT, screen, clock, FPS = window()
    GRAVITY, SCROLL_THRESH, ROWS, COLS, TILE_SIZE, TILE_TYPES, MAX_LEVELS, screen_scroll, background_scroll, level, start_game, start_intro = game_variables(SCREEN_HEIGHT)
    moving_left, moving_right, shoot, grenade, grenade_thrown = player_action_variables()
    start_img, exit_img, restart_img, pine1_img, pine2_img, mountain_img, sky_img, pine1_img, pine2_img, mountain_img, sky_img, bullet_img, grenade_img, health_box_img, ammo_box_img, grenade_box_img, item_boxes = images()
    BACKGROUND, BLACK, WHITE, RED, GREEN, PINK, font = colours_and_font()
    intro_fade, death_fade = screen_fades()
    start_button, exit_button, restart_button = buttons()
    enemy_group, bullet_group, grenade_group, explosion_group, item_box_group, decoration_group, damage_group, next_group = sprite_groups()
    world, player, health_bar = empty_tile_list()




