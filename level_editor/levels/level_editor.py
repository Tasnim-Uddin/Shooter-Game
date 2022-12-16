# https://www.youtube.com/watch?v=-_XnqVsJVIc&list=PLjcN1EyupaQn-x_9QuGIwIESxfV9kNUZf&index=3&ab_channel=CodingWithRuss      5: 00

import pygame
import os
import button

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

# define colours
RED = (200, 25, 25)
GREEN = (144, 201, 120)
WHITE = (255, 255, 255)


# create function for drawing background
def draw_background():
    # scroll is negative because background will move in direction of press, but you want it to go other way (reversed_
    screen.fill(GREEN)
    width = sky_img.get_width()
    for repeat in range(4):
        screen.blit(sky_img, ((repeat * width) - scroll * 0.5, 0))
        screen.blit(mountain_img, ((repeat * width) - scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 150))
        screen.blit(pine1_img, ((repeat * width) - scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 75))
        screen.blit(pine2_img, ((repeat * width) - scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))


# draw grid
def draw_grid():
    # vertical lines
    for c in range(MAX_COLS + 1):
        pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
    # horizontal lines
    for r in range(MAX_COLS + 1):
        pygame.draw.line(screen, WHITE, (0, r * TILE_SIZE), (SCREEN_WIDTH, r * TILE_SIZE))


# create buttons
# make a button list
button_list = []
button_col = 0
button_row = 0
for each_tile in range(len(img_list)):
    tile_button = button.Button(SCREEN_WIDTH + 75 * button_col + 50, 75 * button_row + 50, img_list[each_tile], 1)
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

    # scroll the map
    if scroll_left and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right:
        scroll += 5 * scroll_speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
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
