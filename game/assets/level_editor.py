import pygame
import os
import button
import pickle


pygame.init()

clock = pygame.time.Clock()
FPS = 60

# game window
SCREEN_WIDTH = 650
SCREEN_HEIGHT = 416
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Editor')

# define game variables
ROWS = 16
MAX_COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = len(os.listdir(f'images/tiles'))
level = 1
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

# load images
pine1_img = pygame.image.load('images/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('images/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('images/background/mountain.png').convert_alpha()
sky_img = pygame.image.load('images/background/sky_cloud.png').convert_alpha()

# store tiles in a list
img_list = []
for each_tile in range(TILE_TYPES):
    img = pygame.image.load(f'images/tiles/{each_tile}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

save_img = pygame.image.load('images/buttons/save_button.png').convert_alpha()
load_img = pygame.image.load('images/buttons/load_button.png').convert_alpha()

# define colours
RED = (200, 25, 25)
GREEN = (144, 201, 120)
WHITE = (255, 255, 255)

# define font
font = pygame.font.SysFont('Futura', 25)

# create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * MAX_COLS
    world_data.append(r)

# create ground
for tile in range(0, MAX_COLS):
    world_data[ROWS - 1][tile] = 0


# function for outputting text onto the screen
def draw_text(text, font, text_colour, x, y):
    img = font.render(text, True, text_colour)
    screen.blit(img, (x, y))


# create function for drawing background
def draw_background():
    # scroll is negative because background will move in direction of press, but you want it to go other way (reversed_
    screen.fill(GREEN)
    width = pine2_img.get_width()
    for repeat in range(5):  # how many times background repeats
        screen.blit(sky_img, ((repeat * width) - scroll * 0.5, 0))
        screen.blit(mountain_img, ((repeat * width) - scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 200))
        screen.blit(pine1_img, ((repeat * width) - scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 113))
        screen.blit(pine2_img, ((repeat * width) - scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height() - 2))


# draw grid
def draw_grid():
    # vertical lines
    for y in range(MAX_COLS + 1):
        pygame.draw.line(screen, WHITE, (y * TILE_SIZE - scroll, 0), (y * TILE_SIZE - scroll, SCREEN_HEIGHT))
    # horizontal lines
    for x in range(ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, x * TILE_SIZE), (SCREEN_WIDTH, x * TILE_SIZE))


# function for drawing the world tiles
def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))


# create buttons
save_button = button.Button(x=(SCREEN_WIDTH // 2), y=(SCREEN_HEIGHT + LOWER_MARGIN - 50), image=save_img, scale=1)
load_button = button.Button(x=(SCREEN_WIDTH // 2 + 200), y=(SCREEN_HEIGHT + LOWER_MARGIN - 50), image=load_img, scale=1)

# make a button list
button_list = []
button_col = 0
button_row = 0
for each_tile in range(len(img_list)):
    tile_button = button.Button(x=(SCREEN_WIDTH + 75 * button_col + 50), y=(50 * button_row + 32),
                                image=img_list[each_tile], scale=1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0

run = True
while run:

    clock.tick(FPS)

    draw_background()
    draw_grid()
    draw_world()

    draw_text(text=f'Level: {level}', font=font, text_colour=WHITE, x=10, y=(SCREEN_HEIGHT + LOWER_MARGIN - 90))
    draw_text(text='Press UP or DOWN to change level', font=font, text_colour=WHITE, x=10, y=(SCREEN_HEIGHT + LOWER_MARGIN - 60))

    # save and load data
    if save_button.draw(screen):
        # save level data
        pickle_out = open(f'levels/{level}_data', 'wb')
        pickle.dump(world_data, pickle_out)
        pickle_out.close()

    if load_button.draw(screen):
        # load in level data
        # reset scroll back to the start of the level
        scroll = 0
        world_data = []
        pickle_in = open(f'levels/{level}_data', 'rb')
        world_data = pickle.load(pickle_in)

    # draw tile panel and tiles
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

    # choose a tile
    button_count = 0
    for button_count, each_button in enumerate(button_list):
        if each_button.draw(screen):
            current_tile = button_count

    # highlight the selected tile
    pygame.draw.rect(screen, RED, button_list[current_tile].rect, 2)

    # scroll the map
    if scroll_left and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right and scroll < MAX_COLS * TILE_SIZE - SCREEN_WIDTH:
        scroll += 5 * scroll_speed

    # add new tiles to the screen
    # get mouse position
    # gets tiles number (e.g. tile[5][6])
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // TILE_SIZE  # 0: x coord
    y = pos[1] // TILE_SIZE  # 1: y coord

    # check that the coordinates are within the tile area
    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
        #   update tile value
        if pygame.mouse.get_pressed()[0]:  # 0: left mouse button
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile
        if pygame.mouse.get_pressed()[2]:  # 2: right mouse button
            world_data[y][x] = -1  # -1 means there's nothing there (no tiles)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1
            if event.key == pygame.K_DOWN and level <= 0:
                level = 1
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1

    pygame.display.update()

pygame.quit()
