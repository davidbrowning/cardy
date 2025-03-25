# Full updated code for context (merge this with your existing code)
import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 608
TILE_SIZE = 32
LOG_WIDTH = 100
LOG_MULTIPLIER = 2
TRUCK_WIDTH = TILE_SIZE * 2
ROAD_WIDTH = 128
ROAD_HEIGHT = TILE_SIZE * 3 - 16
ROAD_OFFSET = TILE_SIZE * 2 - 16
ROAD_TOP_OFFSET = TILE_SIZE 
PLATFORM_WIDTH = 80
PLATFORM_HEIGHT = 40
RIVER_TOP = 300
RIVER_BOTTOM = WINDOW_HEIGHT - (TILE_SIZE * 3)
START_Y = WINDOW_HEIGHT - (TILE_SIZE * 2) + 16
GOAL_SIZE = 40
JUMP_DISTANCE = TILE_SIZE 
JUMP_DURATION = 0.5  # seconds
FPS = 60

# Colors
LIGHT_GREEN = (144, 238, 144)
DARK_GREY = (50, 50, 50)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

# Set up the game window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Cardinal Crossing")

# Load assets with try/except
def load_image(filename, size):
    try:
        img = pygame.image.load(filename)
        return pygame.transform.scale(img, size)
    except FileNotFoundError:
        print(f"Warning: {filename} not found.")
        return None

cardinal_left = load_image("cardinal-left.png", (TILE_SIZE, TILE_SIZE))
cardinal_right = load_image("cardinal-right.png", (TILE_SIZE, TILE_SIZE))
trunk_img = load_image("wood-log-trunk.png", (TILE_SIZE * LOG_MULTIPLIER, TILE_SIZE - 2)) 
trunk_face_img = load_image("wood-log-face.png", (TILE_SIZE, TILE_SIZE - 2)) 
trunk_tail_img = load_image("wood-log-tail.png", (TILE_SIZE, TILE_SIZE - 2)) 
log_img = load_image("log.png", (LOG_WIDTH, TILE_SIZE - 2))
water_img = load_image("water.png", (TILE_SIZE, TILE_SIZE))
water_top_img = load_image("water-top.png", (TILE_SIZE, TILE_SIZE))
road_img_top = load_image("road-top.png", (ROAD_WIDTH, ROAD_HEIGHT))
road_img_bottom = load_image("road-bottom.png", (ROAD_WIDTH, ROAD_HEIGHT))
grass_img = load_image("grass.png", (TILE_SIZE, TILE_SIZE))
truck_img_right = load_image("truck-right.png", (TRUCK_WIDTH, TILE_SIZE))
truck_img_left = load_image("truck-left.png", (TRUCK_WIDTH, TILE_SIZE))
platform_img = load_image("platform.png", (PLATFORM_WIDTH, PLATFORM_HEIGHT))
goal_img = load_image("goal.png", (GOAL_SIZE + 10, GOAL_SIZE))

# Load background music
try:
    pygame.mixer.music.load("frogcave.ogg")
    pygame.mixer.music.play(-1)
except FileNotFoundError:
    print("Warning: frogcave.ogg not found.")

# Cardinal properties
cardinal = cardinal_right or pygame.Surface((TILE_SIZE, TILE_SIZE))
cardinal_rect = cardinal.get_rect(center=(WINDOW_WIDTH // 2, START_Y))
target_pos = list(cardinal_rect.topleft)
is_jumping = False
jump_timer = 0

# Log properties
logs = []
for i in range(7):
    log_rect = trunk_img.get_rect() if trunk_img else pygame.Rect(0, 0, LOG_WIDTH, TILE_SIZE)
    log_rect.x = random.randint(0, WINDOW_WIDTH - log_rect.width)
    log_rect.y = RIVER_TOP + 16 + i * (TILE_SIZE) + 5
    speed = (-1 if i % 2 == 0 else 1) * random.choice([2, 4])
    logs.append({"rect": log_rect, "speed": speed})

# Truck properties
trucks = []
for i in range(4):
    truck_rect = truck_img_right.get_rect() if truck_img_right else pygame.Rect(0, 0, TRUCK_WIDTH, TILE_SIZE)
    truck_rect.y = TILE_SIZE * 2 + i * TILE_SIZE
    truck_rect.x = 0
    speed = (-1 if i % 2 == 0 else 1) * random.choice([3, 7])
    trucks.append({"rect": truck_rect, "speed": speed, "is_even": -1 if i % 2 == 0 else 1})

# Goal area
goal_rect = pygame.Rect(WINDOW_WIDTH // 2 - GOAL_SIZE // 2, 10, GOAL_SIZE, GOAL_SIZE)

# Game variables
game_over = False
on_log = False
game_won = False

# Game loop
clock = pygame.time.Clock()
running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # Delta time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and not is_jumping:
            if event.key == pygame.K_LEFT:
                cardinal = cardinal_left or cardinal
                target_pos[0] = cardinal_rect.x - JUMP_DISTANCE
                is_jumping = True
            elif event.key == pygame.K_RIGHT:
                cardinal = cardinal_right or cardinal
                target_pos[0] = cardinal_rect.x + JUMP_DISTANCE
                is_jumping = True
            elif event.key == pygame.K_UP:
                target_pos[1] = cardinal_rect.y - JUMP_DISTANCE
                is_jumping = True
            elif event.key == pygame.K_DOWN:
                target_pos[1] = cardinal_rect.y + JUMP_DISTANCE
                is_jumping = True

    # Smooth jumping
    if is_jumping:
        jump_timer += dt
        progress = min(jump_timer / JUMP_DURATION, 1.0)
        start_pos = [cardinal_rect.x, cardinal_rect.y]
        cardinal_rect.x = start_pos[0] + (target_pos[0] - start_pos[0]) * progress
        cardinal_rect.y = start_pos[1] + (target_pos[1] - start_pos[1]) * progress
        if progress >= 1.0:
            is_jumping = False
            jump_timer = 0
            cardinal_rect.topleft = target_pos

    # Update logs
    on_log = False
    for log in logs:
        log["rect"].x += log["speed"]
        if log["rect"].x > WINDOW_WIDTH:
            log["rect"].x = -log["rect"].width
        elif log["rect"].x < -log["rect"].width:
            log["rect"].x = WINDOW_WIDTH
        if cardinal_rect.colliderect(log["rect"]) and RIVER_TOP <= cardinal_rect.y <= RIVER_BOTTOM:
            on_log = True
            cardinal_rect.x += log["speed"]
            target_pos[0] += log["speed"]
        if on_log:
            target_pos[0] = cardinal_rect.x

    # Update trucks
    for truck in trucks:
        truck["rect"].x += truck["speed"]
        if truck["rect"].x > WINDOW_WIDTH:
            truck["rect"].x = -truck["rect"].width
        elif truck["rect"].x < -truck["rect"].width:
            truck["rect"].x = WINDOW_WIDTH
        if cardinal_rect.colliderect(truck["rect"]):
            game_over = True

    # Check water and goal
    if not is_jumping:  # Only check water when jump is complete
        if RIVER_TOP <= cardinal_rect.y <= RIVER_BOTTOM and not on_log:
            game_over = True
    if cardinal_rect.colliderect(goal_rect):
        game_won = True

    # Keep cardinal in bounds
    cardinal_rect.clamp_ip(window.get_rect())
    if not is_jumping:
        target_pos = list(cardinal_rect.topleft)

    # Draw everything
    window.fill(LIGHT_GREEN)
    if grass_img:
        for x in range(0, WINDOW_WIDTH, TILE_SIZE):
            for y in range(0, RIVER_TOP, TILE_SIZE):
                window.blit(grass_img, (x, y))
            for y in range(RIVER_BOTTOM + TILE_SIZE, WINDOW_HEIGHT, TILE_SIZE):
                window.blit(grass_img, (x, y))
    else:
        pygame.draw.rect(window, (0, 128, 0), (0, 0, WINDOW_WIDTH, RIVER_TOP))
        pygame.draw.rect(window, (0, 128, 0), (0, RIVER_BOTTOM, WINDOW_WIDTH, WINDOW_HEIGHT - RIVER_BOTTOM))
        
    # Draw highway
    for x in range(0, WINDOW_WIDTH, ROAD_WIDTH):
        if road_img_top:
            window.blit(road_img_top, (x, ROAD_HEIGHT - ROAD_TOP_OFFSET))
        if road_img_bottom:
            window.blit(road_img_bottom, (x, ROAD_HEIGHT + ROAD_OFFSET))

    # Draw river
    if water_top_img:
        for x in range(0, WINDOW_WIDTH, TILE_SIZE):
            window.blit(water_top_img, (x, RIVER_TOP))
    if water_img:
        for x in range(0, WINDOW_WIDTH, TILE_SIZE):
            for y in range(RIVER_TOP + TILE_SIZE, RIVER_BOTTOM + TILE_SIZE, TILE_SIZE):
                window.blit(water_img, (x, y))

    # Draw logs and trucks
    for log in logs:
        if trunk_img:
            window.blit(trunk_img, log["rect"])
            # Calculate the new position for the face, offset by 16 pixels downward
            face_x = log["rect"].x - 22
            face_y = log["rect"].y
            window.blit(trunk_face_img, (face_x, face_y))
            tail_x = log["rect"].x + (TILE_SIZE * LOG_MULTIPLIER)
            tail_y = log["rect"].y
            window.blit(trunk_tail_img, (tail_x, tail_y))
            # Draw the face at the offset position
    for truck in trucks:
        if truck["is_even"] == -1 and truck_img_left:
            window.blit(truck_img_left, truck["rect"])
        elif truck["is_even"] == 1 and truck_img_right:
            window.blit(truck_img_right, truck["rect"])

    # Draw goal and platform
    if goal_img:
        window.blit(goal_img, goal_rect)
    else:
        pygame.draw.rect(window, (0, 255, 0), goal_rect)
    if platform_img:
        window.blit(platform_img, (WINDOW_WIDTH // 2 - PLATFORM_WIDTH // 2, START_Y - (TILE_SIZE / 2)))
    else:
        pygame.draw.rect(window, (150, 150, 150), (WINDOW_WIDTH // 2 - PLATFORM_WIDTH // 2, START_Y, PLATFORM_WIDTH, PLATFORM_HEIGHT))

    #for i in range(math.floor(WINDOW_HEIGHT / 32)):
    #    pygame.draw.rect(window, WHITE, (0, i * 32, WINDOW_WIDTH, 1))


    # Draw cardinal
    # pygame.draw.rect(window, (128, 0, 0), cardinal_rect)
    window.blit(cardinal, cardinal_rect)

    # Game over or win
    if game_over or game_won:
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over!" if game_over else "You Win!", True, (255, 0, 0) if game_over else (0, 255, 0))
        window.blit(text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        break

    pygame.display.flip()

pygame.quit()