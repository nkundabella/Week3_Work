import utils.session
import pygame
import serial
import random

SERIAL_PORT = 'COM5'  
BAUD_RATE = 115200

pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Colors
SKY_BLUE = (135, 206, 235)
BOOK_RED = (150, 40, 40)
PAGE_WHITE = (245, 245, 245)

# Game Variables
smooth_pitch, smooth_roll = 0, 0
lerp_factor = 0.1
score = 0
game_over = False
obstacles = []

class Obstacle:
    def __init__(self):
        self.x = width + 50
        self.y = random.randint(50, height - 50)
        self.size = random.randint(30, 60)
        
    def move(self):
        self.x -= 5 

    def display(self):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.size, self.size))

def draw_book(x, y):
    # Book Cover
    pygame.draw.rect(screen, BOOK_RED, (x-30, y-40, 60, 80), border_radius=4)
    # Pages (white sliver on the side)
    pygame.draw.rect(screen, PAGE_WHITE, (x+20, y-35, 5, 70))
    # Spine line
    pygame.draw.line(screen, (0, 0, 0), (x-28, y-40), (x-28, y+40), 2)

# Serial Connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
except Exception as e:
    print(f"Error connecting: {e}")
    exit()

running = True
while running:
    screen.fill(SKY_BLUE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r: # Restart logic [cite: 28]
                game_over = False
                score = 0
                obstacles = []

    if not game_over:
        # 1. READ SERIAL DATA [cite: 30, 62]
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                parts = line.split(',')
                if len(parts) == 2:
                    # Lerp/Smoothing logic from original code [cite: 17, 43]
                    target_pitch = float(parts[0])
                    target_roll = float(parts[1])
                    smooth_pitch += (target_pitch - smooth_pitch) * lerp_factor
                    smooth_roll += (target_roll - smooth_roll) * lerp_factor
            except:
                pass

        # 2. MAP DATA TO POSITION [cite: 19, 44]
        # Map -45/45 degrees to screen bounds
        char_y = int((smooth_pitch + 45) * (height / 90))
        char_x = int((smooth_roll + 45) * (width / 90))
        
        # 3. OBSTACLE LOGIC [cite: 21, 22]
        if random.random() < 0.03: # Spawn chance
            obstacles.append(Obstacle())

        for obs in obstacles[:]:
            obs.move()
            obs.display()
            
            # Collision [cite: 23, 49]
            if abs(char_x - obs.x) < 40 and abs(char_y - obs.y) < 40:
                game_over = True
                
            if obs.x < -50:
                obstacles.remove(obs)
                score += 1 [cite: 24]

        draw_book(char_x, char_y)
        
        # UI
        font = pygame.font.SysFont(None, 30)
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
    else:
        font = pygame.font.SysFont(None, 50)
        text = font.render("GAME OVER - Press R to Restart", True, (0, 0, 0))
        screen.blit(text, (width//2 - 250, height//2))

    pygame.display.flip()
    clock.tick(60)

ser.close()
pygame.quit()