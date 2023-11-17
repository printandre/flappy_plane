import pygame
from pygame.locals import *
import random

# Initialize Pygame
pygame.init()

# Define a way to count fps
clock = pygame.time.Clock()
fps = 60

screen_width = 563
screen_height = 650

# Create Pygame screen and title (width and height due to background sprite)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Plane")

# Define font and colors
font = pygame.font.SysFont('Bauhaus 93', 60)
white = (255, 255, 255)
dark_purple = (64, 0, 64)
purple = (128, 0, 128)

#Define start and end messages
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def show_start_message():
    draw_text("Non farti colpire!", font, purple, screen_width / 12, screen_height // 3)
    draw_text("Premi SPACE", font, purple, screen_width / 6, (2 * screen_height) // 4)

def show_end_message():
    draw_text("Game over", font, purple, screen_width / 4, screen_height // 3)
    draw_text("Premi ENTER per ricominciare", pygame.font.SysFont('Bauhaus 93', 30), purple, screen_width / 8, (2 * screen_height) // 4)


# Define game variables
ground_scroll = 0
scroll_speed = 6
#Set game_over as a global variable
flying = False
global game_over 
game_over = False
#Set variables for handling torpedos frequency
torpedo_frequency = 500 #milliseconds
last_torpedo = pygame.time.get_ticks() - torpedo_frequency 
#Set variables for score
score = 0
passed_torpedos = 0
#Set variable for sound
explosion_played = False
song_on = True

# Load images
background = pygame.image.load(r'pic\sky.jpg')
ground = pygame.image.load(r'pic\ground.png')

# Load sounds
song = pygame.mixer.Sound(r'sounds\TimTaj - Happy Ramadan Days.mp3')
explosion_sound = pygame.mixer.Sound(r'sounds\explosion_01.wav')

def reset_game():
    hitbox_group.empty()
    torpedo_group.empty()
    explosion_group.empty()
    plane.rect.x = 80
    plane.rect.y = 680

class Plane(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = {
            'upright': pygame.image.load(r'pic\plane.png'),
            'rotate_up': pygame.transform.rotate(pygame.image.load(r'pic\plane.png'), 5),
            'rotate_down': pygame.transform.rotate(pygame.image.load(r'pic\plane.png'), -5)
        }
        self.state = 'upright'
        self.image = self.images[self.state]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        global game_over #modifying the global game_over variable
        if not game_over and flying == True:
            # Apply gravity to the rect
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            self.rect.y += self.vel

            # Implement jump with space keyboard
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not self.clicked:
                self.clicked = True
                self.vel = -10
                self.state = 'rotate_up'
            elif not keys[pygame.K_SPACE]:  # Jump only if the spacebar is released
                self.clicked = False
                self.state = 'rotate_down' if self.vel >= 0 else 'rotate_up'

        # Limit the plane's position to the screen boundaries
        if self.rect.bottom >= 480:
            self.rect.bottom = 480
            self.state = 'upright'  # Reset rotation when the plane hits the ground
        elif self.rect.top <= 10:
            self.rect.top = 10
            self.state = 'upright'  # Reset rotation when the plane hits the ceiling

        # Update the image based on the current state
        self.image = self.images[self.state]

        # Update the rect to keep it centered correctly after rotation
        self.rect = self.image.get_rect(center=self.rect.center)

class Torpedo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = [
            pygame.image.load(r'pic\torpedo1.png'),
            pygame.image.load(r'pic\torpedo2.png'),
            pygame.image.load(r'pic\torpedo3.png'),
            pygame.image.load(r'pic\torpedo4.png'),
            pygame.image.load(r'pic\torpedo5.png'),
        ]
        self.image = random.choice(self.images)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.passed = False
    
    def update(self):
        # Move the torpedo to the left (scrolling effect)
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()  # Remove the torpedo when it's off-screen
        
class Hitbox(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(r'pic\hitbox.jpg')
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
    # Move the hitbox to the left (scrolling effect)
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()  # Remove the hitbox when it's off-screen

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []  # List to store explosion images
        self.index = 0  # Index to keep track of the current image
        self.load_images()  # Load explosion images
        self.image = self.images[self.index]  # Set the initial image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def load_images(self):
        # Load explosion images
        for i in range(1, 5):
            path = f'pic\keyframes\explosion_0{i}.png'
            image = pygame.image.load(path)
            self.images.append(image)

    def update(self):
        self.index += 1
        if self.index >= len(self.images):
            self.kill()  # Remove the explosion when the animation is complete
        else: 
            self.image = self.images[self.index]

# Create a sprite group for classes
plane_group = pygame.sprite.Group()
torpedo_group = pygame.sprite.Group()
hitbox_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

plane = Plane(80, 680)  # Initial position
plane_group.add(plane)

# Game loop
game_started = False
run = True
while run:
    clock.tick(fps)

    # draw elements
    screen.blit(background, (0, 0))
    plane_group.draw(screen)
    torpedo_group.draw(screen)
    plane_group.update()

    # Set song
    if song_on:
        song.play()
        song_on = False

    # Draw the ground image multiple times for scrolling effect
    screen.blit(ground, (ground_scroll, 330))
    screen.blit(ground, (ground_scroll + ground.get_width(), 330))

    #check the score
    for torpedo in torpedo_group:
        if plane.rect.centerx > torpedo.rect.centerx and not torpedo.passed:
            torpedo.passed = True
            passed_torpedos += 1
            # Check if 5 torpedos have been passed
            if passed_torpedos >= 5:
                score += 1                
                passed_torpedos = 0  # Reset the counter
                #Increase velocity
                if score % 5 == 0:
                    scroll_speed += 1

    #draw score
    draw_text(str(score), font, white, int(screen_width / 2.1), 20)
            
    #look for collision
    if pygame.sprite.groupcollide(plane_group, hitbox_group, False, False):
        song.stop()
        if not explosion_played:
            explosion_sound.play()
            explosion_played = True

        explosion = Explosion(plane.rect.centerx, plane.rect.centery)
        explosion_group.add(explosion)
        game_over = True
        flying = False 

    explosion_group.draw(screen)
    explosion_group.update()

    if game_over == False and flying == True:
        # Generate new torpedos
        time_now = pygame.time.get_ticks()
        if time_now - last_torpedo > torpedo_frequency:
            torpedo = Torpedo(screen_width + 50, random.randint(40, 500))
            hit = Hitbox(screen_width + 20 ,torpedo.rect.centery -10)
            torpedo_group.add(torpedo)
            hitbox_group.add(hit)
            last_torpedo = time_now

        #scroll the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > ground.get_width():
            ground_scroll = 0

        torpedo_group.update()
        hitbox_group.update()
    
    #show messages
    if not game_started:
        show_start_message()
    if game_over:
        show_end_message()

    # Handle events
    for event in pygame.event.get():
        #Handle window
        if event.type == pygame.QUIT:
            run = False
        #Handle different keys
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            if not game_started and event.key == pygame.K_SPACE and not game_over:
                game_started = True
                flying = True
            elif event.key == K_RETURN and game_over: #Press enter key for restarting the game
                game_over = False
                reset_game()
                explosion_sound.stop()
                score = 0 
                explosion_played = False
                flying = True
                song_on = True 
                scroll_speed = 6

    # Refresh the display
    pygame.display.update()

pygame.quit()