import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
TILE_SIZE = 32
LOG_WIDTH = 100
TRUCK_WIDTH = 64
ROAD_WIDTH = 128
ROAD_HEIGHT = 64
PLATFORM_WIDTH = 80
PLATFORM_HEIGHT = 40
RIVER_TOP = 300
RIVER_BOTTOM = 500
START_Y = 520
GOAL_SIZE = 40
JUMP_DISTANCE = TILE_SIZE
JUMP_DURATION = 0.5  # seconds
FPS = 60

# Colors
LIGHT_GREEN = (144, 238, 144)
DARK_GREY = (50, 50, 50)
YELLOW = (255, 255, 0)

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
log_img = load_image("log.png", (LOG_WIDTH, TILE_SIZE))
water_img = load_image("water.png", (TILE_SIZE, TILE_SIZE))
water_top_img = load_image("water-top.png", (TILE_SIZE, TILE_SIZE))
road_img_top = load_image("road-top.png", (ROAD_WIDTH, ROAD_HEIGHT))
road_img_bottom = load_image("road-bottom.png", (ROAD_WIDTH, ROAD_HEIGHT))
grass_img = load_image("grass.png", (TILE_SIZE, TILE_SIZE))
truck_img_right = load_image("truck-right.png", (TRUCK_WIDTH, TILE_SIZE))
truck_img_left = load_image("truck-left.png", (TRUCK_WIDTH, TILE_SIZE))
platform_img = load_image("platform.png", (PLATFORM_WIDTH, PLATFORM_HEIGHT))
goal_img = load_image("goal.png", (TILE_SIZE, TILE_SIZE))

# Load background music
try:
    pygame.mixer.music.load("frogcave.ogg")
    pygame.mixer.music.play(-1)
except FileNotFoundError:
    print("Warning: frogcave.ogg not found.")

# Cardinal properties
cardinal = cardinal_right or pygame.Surface((TILE_SIZE, TILE_SIZE))  # Fallback
cardinal_rect = cardinal.get_rect(center=(WINDOW_WIDTH // 2, START_Y))
target_pos = list(cardinal_rect.topleft)
is_jumping = False
jump_timer = 0

# Log properties
logs = []
for i in range(6):
    log_rect = log_img.get_rect() if log_img else pygame.Rect(0, 0, LOG_WIDTH, TILE_SIZE)
    log_rect.x = random.randint(0, WINDOW_WIDTH - log_rect.width)
    log_rect.y = RIVER_TOP + 20 + i * TILE_SIZE + 5
    speed = (-1 if i % 2 == 0 else 1) * random.choice([1, 2])
    logs.append({"rect": log_rect, "speed": speed})

# Truck properties
trucks = []
for i in range(4):
    truck_rect = truck_img_right.get_rect() if truck_img_right else pygame.Rect(0, 0, TRUCK_WIDTH, TILE_SIZE)
    truck_rect.y = TILE_SIZE * 2 + i * TILE_SIZE
    truck_rect.x = 0
    speed = (-1 if i % 2 == 0 else 1) * random.choice([1, 5])
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
                target_pos[0] = cardinal_rect.x - JUMP_DISTANCE  # Full tile left
                is_jumping = True
            elif event.key == pygame.K_RIGHT:
                cardinal = cardinal_right or cardinal
                target_pos[0] = cardinal_rect.x + JUMP_DISTANCE  # Full tile right
                is_jumping = True
            elif event.key == pygame.K_UP:
                target_pos[1] = cardinal_rect.y - JUMP_DISTANCE  # Full tile up
                is_jumping = True
            elif event.key == pygame.K_DOWN:
                target_pos[1] = cardinal_rect.y + JUMP_DISTANCE  # Full tile down
                is_jumping = True
    # Smooth jumping (replace the existing jumping block)
    if is_jumping:
        jump_timer += dt
        progress = min(jump_timer / JUMP_DURATION, 1.0)  # 0 to 1 over 0.5s
        start_pos = [cardinal_rect.x, cardinal_rect.y]  # Current position
        cardinal_rect.x = start_pos[0] + (target_pos[0] - start_pos[0]) * progress
        cardinal_rect.y = start_pos[1] + (target_pos[1] - start_pos[1]) * progress
        if progress >= 1.0:
            is_jumping = False
            jump_timer = 0
            cardinal_rect.topleft = target_pos  # Snap to exact tile at end
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
            target_pos[0] = cardinal_rect.x  # Sync target with new position

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
    if RIVER_TOP <= cardinal_rect.y <= RIVER_BOTTOM and not on_log:
        game_over = True
    if cardinal_rect.colliderect(goal_rect):
        game_won = True

    # Before drawing, keep cardinal in bounds (update this part)
    cardinal_rect.clamp_ip(window.get_rect())
    if not is_jumping:  # Only sync target when not jumping
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
            window.blit(road_img_top, (x, TILE_SIZE * 2))
        if road_img_bottom:
            window.blit(road_img_bottom, (x, TILE_SIZE * 4 + 16))

    # Draw river
    if water_top_img:
        for x in range(0, WINDOW_WIDTH, TILE_SIZE):
            window.blit(water_top_img, (x, RIVER_TOP))
    if water_img:
        for x in range(0, WINDOW_WIDTH, TILE_SIZE):
            for y in range(RIVER_TOP + TILE_SIZE, RIVER_BOTTOM, TILE_SIZE):
                window.blit(water_img, (x, y))

    # Draw logs and trucks
    for log in logs:
        if log_img:
            window.blit(log_img, log["rect"])
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
        window.blit(platform_img, (WINDOW_WIDTH // 2 - PLATFORM_WIDTH // 2, START_Y))
    else:
        pygame.draw.rect(window, (150, 150, 150), (WINDOW_WIDTH // 2 - PLATFORM_WIDTH // 2, START_Y, PLATFORM_WIDTH, PLATFORM_HEIGHT))

    # Draw cardinal
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