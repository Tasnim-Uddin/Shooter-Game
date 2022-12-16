# https://www.youtube.com/watch?v=G8MYGDf_9ho        4: 00


import pygame

# create display window
SCREEN_HEIGHT = 500
SCREEN_WIDTH = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Button Maker')

# load button images
start_img = pygame.image.load('images/start_button.png').convert_alpha()
exit_img = pygame.image.load('images/exit_button.png').convert_alpha()


# button class
class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] and not self.clicked:  # [0] is left click
                self.clicked = True
                action = True

        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        # draw button on screen
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

# create button instances
start_button = Button(x=100, y=200, image=start_img, scale=0.8)
exit_button = Button(x=450, y=200, image=exit_img, scale=0.8)

# game loop
run = True
while run:

    screen.fill((202, 228, 241))

    if start_button.draw():
        print('START')
    if exit_button.draw():
        run = False
        # print('EXIT')

    # event handler
    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
