import pygame
import sys
import random

# --- CONSTANTS ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
GRID_SIZE = 40
FPS = 60

# --- VOXEL PALETTE ---
SKY_BLUE = (135, 206, 235)
GRASS_TOP = (164, 231, 106)
GRASS_SIDE = (136, 197, 86)
ROAD_GRAY = (66, 76, 88)
ROAD_MARKING = (255, 255, 255)
SHADOW = (0, 0, 0, 50)
TREE_TOP = (76, 209, 55)
TREE_SIDE = (39, 142, 18)
TRUNK = (139, 69, 19)

# Colors
WHITE = (255, 255, 255)
CHICKEN_BODY = (255, 255, 255)
CHICKEN_BEAK = (255, 165, 0)
CHICKEN_COMB = (255, 0, 0)
CAR_COLORS = [(231, 76, 60), (52, 152, 219), (241, 196, 15), (155, 89, 182)]
GOLD_COLOR = (255, 215, 0)
SHIELD_COLOR = (0, 191, 255)

# --- PARTICLE CLASS ---
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-6, 2)
        self.color = random.choice([CHICKEN_BODY, CHICKEN_BEAK, CHICKEN_COMB])
        self.size = random.randint(4, 8)
        self.life = random.randint(30, 60)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            alpha = int((self.life / 60) * 255)
            s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.rect(s, SHADOW, (1, 1, self.size, self.size), border_radius=2)
            pygame.draw.rect(s, (*self.color, alpha), (0, 0, self.size-1, self.size-1), border_radius=2)
            surface.blit(s, (self.x, self.y))

# --- COLLECTIBLE CLASS ---
class Collectible:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x + 10, y + 10, 20, 20)
        self.type = type
        self.y_offset = 0
        self.bob_direction = 1

    def update(self):
        self.y_offset += 0.5 * self.bob_direction
        if abs(self.y_offset) > 3: self.bob_direction *= -1

    def draw(self, surface):
        draw_y = self.rect.y + self.y_offset
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(s, SHADOW, (0, 15, 20, 5))
        surface.blit(s, (self.rect.x, draw_y + 5))

        if self.type == 'Coin':
            pygame.draw.circle(surface, GOLD_COLOR, (self.rect.centerx, int(draw_y + 10)), 10)
            pygame.draw.circle(surface, (255, 223, 0), (self.rect.centerx, int(draw_y + 10)), 7)
        elif self.type == 'Shield':
            pygame.draw.circle(surface, SHIELD_COLOR, (self.rect.centerx, int(draw_y + 10)), 10)
            pygame.draw.rect(surface, WHITE, (self.rect.centerx - 3, int(draw_y + 5), 6, 10))
            pygame.draw.rect(surface, WHITE, (self.rect.centerx - 7, int(draw_y + 8), 14, 4))

class Player:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.reset()

    def reset(self):
        self.x = (SCREEN_WIDTH // 2 // GRID_SIZE) * GRID_SIZE + 5
        self.y = (SCREEN_HEIGHT // 2) + (GRID_SIZE * 3) + 5 
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.alive = True
        self.has_shield = False
        self.invincible_timer = 0

    def trigger_shield(self):
        self.has_shield = False
        self.invincible_timer = 120 

    def move(self, dx, dy):
        if not self.alive: return
        self.x += dx * GRID_SIZE
        self.y += dy * GRID_SIZE
        self.x = max(5, min(self.x, SCREEN_WIDTH - GRID_SIZE + 5))
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        if not self.alive: return
        
        if self.has_shield:
            pygame.draw.circle(surface, (0, 191, 255, 100), self.rect.center, 22, width=2)
        
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            if (self.invincible_timer // 5) % 2 == 0: return 

        s = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(s, SHADOW, (5, 5, 30, 25), border_radius=4)
        surface.blit(s, self.rect)
        pygame.draw.rect(surface, CHICKEN_BODY, self.rect, border_radius=4)
        pygame.draw.rect(surface, CHICKEN_COMB, (self.rect.centerx - 3, self.rect.y + 2, 6, 4))
        pygame.draw.rect(surface, CHICKEN_BEAK, (self.rect.centerx + 2, self.rect.centery - 2, 8, 4))
        pygame.draw.rect(surface, (0,0,0), (self.rect.centerx + 4, self.rect.centery - 8, 4, 4))

class Car:
    def __init__(self, x, y, speed, direction):
        self.rect = pygame.Rect(x, y + 8, 50, 24)
        self.speed = speed * direction
        self.color = random.choice(CAR_COLORS)
        r, g, b = self.color
        self.roof_color = (min(255, r+40), min(255, g+40), min(255, b+40))

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > SCREEN_WIDTH + 60: self.rect.x = -60
        if self.rect.x < -60: self.rect.x = SCREEN_WIDTH + 60

    def draw(self, surface):
        s = pygame.Surface((50, 24), pygame.SRCALPHA)
        pygame.draw.rect(s, SHADOW, (5, 5, 50, 24), border_radius=5)
        surface.blit(s, self.rect)
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
        pygame.draw.rect(surface, self.roof_color, (self.rect.x + 5, self.rect.y, 35, 18), border_radius=3)
        win_x = self.rect.right - 12 if self.speed > 0 else self.rect.left + 4
        pygame.draw.rect(surface, (200, 240, 255), (win_x, self.rect.y + 2, 8, 20))

class Tree:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 5, y - 20, 30, 50) 
        self.hitbox = pygame.Rect(x + 5, y, 30, 30)
    
    def draw(self, surface):
        s = pygame.Surface((30, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(s, SHADOW, (0, 0, 30, 20))
        surface.blit(s, (self.rect.x, self.rect.bottom - 15))
        pygame.draw.rect(surface, TRUNK, (self.rect.centerx - 6, self.rect.bottom - 20, 12, 20))
        pygame.draw.rect(surface, TREE_SIDE, (self.rect.x, self.rect.y + 10, 30, 30), border_radius=2)
        pygame.draw.rect(surface, TREE_TOP, (self.rect.x, self.rect.y, 30, 10), border_radius=2)

class Lane:
    def __init__(self, y, type, exclude_center=False):
        self.y = y
        self.type = type
        self.cars = []
        self.trees = []
        self.items = []
        
        center_x = SCREEN_WIDTH // 2

        if type == 'Road':
            direction = random.choice([-1, 1])
            speed = random.randint(2, 5)
            for i in range(random.randint(1, 2)):
                self.cars.append(Car(random.randint(0, SCREEN_WIDTH), self.y, speed, direction))
            
            # --- UPDATED: Coins appear ~8% of the time on roads
            if random.random() < 0.08:
                self.items.append(Collectible(random.randint(0, 14) * GRID_SIZE, self.y, 'Coin'))

        elif type == 'Grass':
            for i in range(0, SCREEN_WIDTH, GRID_SIZE):
                if exclude_center and abs(i - center_x) < GRID_SIZE:
                    continue

                rand_val = random.random()
                
                # --- UPDATED SPAWN RATES ---
                if rand_val < 0.20: 
                    self.trees.append(Tree(i, self.y)) # 20% Trees
                elif rand_val < 0.23: 
                    self.items.append(Collectible(i, self.y, 'Shield')) # ~3% Shields
                elif rand_val < 0.30: 
                    self.items.append(Collectible(i, self.y, 'Coin')) # ~7% Coins

    def update(self):
        for car in self.cars: car.update()
        for item in self.items: item.update()

    def draw(self, surface):
        if self.type == 'Grass':
            pygame.draw.rect(surface, GRASS_TOP, (0, self.y, SCREEN_WIDTH, GRID_SIZE))
            pygame.draw.rect(surface, GRASS_SIDE, (0, self.y + GRID_SIZE - 6, SCREEN_WIDTH, 6))
            for item in self.items: item.draw(surface)
            for tree in self.trees: tree.draw(surface)
        else:
            pygame.draw.rect(surface, ROAD_GRAY, (0, self.y, SCREEN_WIDTH, GRID_SIZE))
            for i in range(10, SCREEN_WIDTH, 60):
                pygame.draw.rect(surface, ROAD_MARKING, (i, self.y + 18, 30, 4))
            for item in self.items: item.draw(surface)
            for car in self.cars: car.draw(surface)

def draw_text(surface, text, size, y, color=(255, 255, 255)):
    font = pygame.font.SysFont("Arial", size, bold=True)
    text_surf = font.render(text, True, color)
    rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, y))
    surface.blit(text_surf, rect)

def draw_ui(screen, score, state, player):
    if state == "START":
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0,0))
        draw_text(screen, "CROSSY ROAD", 60, SCREEN_HEIGHT//2 - 50)
        draw_text(screen, "PRESS ARROWS TO START", 30, SCREEN_HEIGHT//2 + 20)
    elif state == "PLAYING":
        pygame.draw.rect(screen, WHITE, (20, 20, 120, 40), border_radius=20)
        font = pygame.font.SysFont("Arial", 28, bold=True)
        text = font.render(f"{score}", True, (50, 50, 50))
        screen.blit(text, (50, 25))
        
        if player.has_shield:
            pygame.draw.circle(screen, SHIELD_COLOR, (160, 40), 15)
            pygame.draw.rect(screen, WHITE, (157, 35, 6, 10)) 
            pygame.draw.rect(screen, WHITE, (153, 38, 14, 4))

    elif state == "GAME_OVER":
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0,0))
        draw_text(screen, "GAME OVER", 60, SCREEN_HEIGHT//2 - 40, (255, 100, 100))
        draw_text(screen, f"SCORE: {score}", 40, SCREEN_HEIGHT//2 + 20)
        draw_text(screen, "PRESS SPACE TO RESTART", 20, SCREEN_HEIGHT//2 + 70)

def is_blocked(lanes, target_x, target_y):
    target_rect = pygame.Rect(target_x, target_y, 30, 30)
    for lane in lanes:
        if abs(lane.y - target_y) < 50:
            for tree in lane.trees:
                if target_rect.colliderect(tree.hitbox): return True
    return False

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Crossy Road - Final")
    clock = pygame.time.Clock()
    
    player = Player()
    lanes = []
    particles = []
    score = 0
    game_state = "START"

    current_y = SCREEN_HEIGHT
    grass_streak = 0
    while current_y > -100:
        if current_y > player.y - 100: 
            type = 'Grass'
        else:
            if grass_streak >= 2: type = 'Road'; grass_streak = 0
            else: type = random.choice(['Grass', 'Road', 'Road'])
        
        if type == 'Grass': grass_streak += 1
        else: grass_streak = 0
        
        is_start_zone = abs(current_y - player.y) < GRID_SIZE
        lanes.append(Lane(current_y, type, exclude_center=is_start_zone))
        
        current_y -= GRID_SIZE

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_state == "START": game_state = "PLAYING"
                elif game_state == "GAME_OVER": 
                    if event.key == pygame.K_SPACE: main()
                elif game_state == "PLAYING":
                    if event.key == pygame.K_UP:
                        target_y = player.y - GRID_SIZE
                        if not is_blocked(lanes, player.x, target_y):
                            score += 1
                            for lane in lanes:
                                lane.y += GRID_SIZE
                                for car in lane.cars: car.rect.y += GRID_SIZE
                                for tree in lane.trees: tree.rect.y += GRID_SIZE
                                for tree in lane.trees: tree.hitbox.y += GRID_SIZE
                                for item in lane.items: item.rect.y += GRID_SIZE
                            
                            top_lane_y = lanes[-1].y
                            new_y = top_lane_y - GRID_SIZE
                            new_type = random.choice(['Grass', 'Road'])
                            lanes.append(Lane(new_y, new_type)) 
                            if lanes[0].y > SCREEN_HEIGHT: lanes.pop(0)
                            
                    elif event.key == pygame.K_LEFT: 
                        target_x = player.x - GRID_SIZE
                        if not is_blocked(lanes, target_x, player.y): player.move(-1, 0)
                    elif event.key == pygame.K_RIGHT: 
                        target_x = player.x + GRID_SIZE
                        if not is_blocked(lanes, target_x, player.y): player.move(1, 0)

        if game_state == "PLAYING":
            for lane in lanes:
                lane.update()
                
                for item in lane.items[:]:
                    if player.rect.colliderect(item.rect):
                        if item.type == 'Coin':
                            score += 5
                            lane.items.remove(item)
                        elif item.type == 'Shield' and not player.has_shield:
                            player.has_shield = True
                            lane.items.remove(item)

                if lane.type == 'Road' and player.invincible_timer == 0:
                    for car in lane.cars:
                        hitbox = car.rect.inflate(-10, -10)
                        if player.rect.colliderect(hitbox):
                            if player.has_shield:
                                player.trigger_shield()
                            else:
                                player.alive = False
                                game_state = "GAME_OVER"
                                for _ in range(40):
                                    particles.append(Particle(player.rect.centerx, player.rect.centery))

        for p in particles[:]:
            p.update()
            if p.life <= 0: particles.remove(p)

        screen.fill(SKY_BLUE)
        for lane in lanes: lane.draw(screen)
        player.draw(screen)
        for p in particles: p.draw(screen)
        draw_ui(screen, score, game_state, player)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()