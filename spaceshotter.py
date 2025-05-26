import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Game settings
ENEMY_SPAWN_RATE = 2000  # milliseconds
BULLET_SPEED = 10
ENEMY_SPEED = 3

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = BULLET_SPEED

    def update(self):
        # Move the bullet upward
        self.rect.y -= self.speed
        # Remove the bullet if it goes off-screen
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create a simple enemy ship (a rectangle for now)
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        
        # Random starting position at the top
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        
        # Random speed (within a range)
        self.speed = random.randrange(1, ENEMY_SPEED + 1)

    def update(self):
        # Move the enemy downward
        self.rect.y += self.speed
        # Respawn if it goes off the bottom of the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed = random.randrange(1, ENEMY_SPEED + 1)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create a simple spaceship (a rectangle for now)
        self.image = pygame.Surface((50, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        
        # Set initial position at the bottom center of the screen
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        
        # Movement speed
        self.speed = 8
        
        # Shooting cooldown
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 250  # milliseconds between shots
        
    def update(self):
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Move left/right
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
    
    def shoot(self):
        # Check if enough time has passed since the last shot
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            return True
        return False

def draw_text(surface, text, size, x, y):
    """Helper function to draw text on screen"""
    font = pygame.font.Font(pygame.font.match_font('arial'), size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def main():
    # Set up the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Shooter")
    
    # Set up the clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    
    # Create the player
    player = Player()
    all_sprites.add(player)
    
    # Create initial enemies
    for i in range(8):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
    
    # Set up for enemy spawning
    last_enemy_spawn = pygame.time.get_ticks()
    
    # Setup scoring
    score = 0
    
    # Game loop
    running = True
    while running:
        # Keep the loop running at the right speed
        clock.tick(FPS)
        now = pygame.time.get_ticks()
        
        # Process input (events)
        for event in pygame.event.get():
            # Check for closing the window
            if event.type == pygame.QUIT:
                running = False
            # Check for key presses
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Check for shooting
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if player.shoot():
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
        
        # Spawn new enemies periodically
        if now - last_enemy_spawn > ENEMY_SPAWN_RATE:
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)
            last_enemy_spawn = now
        
        # Update game objects
        all_sprites.update()
        
        # Check for collisions between bullets and enemies
        hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
        for hit in hits:
            # Spawn a new enemy for each destroyed enemy
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)
            # Increase score
            score += 10
        
        # Check for collisions between player and enemies
        hits = pygame.sprite.spritecollide(player, enemies, False)
        if hits:
            # Game over
            running = False
        
        # Draw / render
        screen.fill(BLACK)  # Fill the screen with black
        all_sprites.draw(screen)  # Draw all sprites
        
        # Draw the score
        draw_text(screen, f"Score: {score}", 24, SCREEN_WIDTH // 2, 10)
        
        # Display what we've drawn
        pygame.display.flip()
    
    # Game over screen
    screen.fill(BLACK)
    draw_text(screen, "GAME OVER", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    draw_text(screen, f"Final Score: {score}", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text(screen, "Press ESC to quit", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
    pygame.display.flip()
    
    # Wait for player to exit
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
