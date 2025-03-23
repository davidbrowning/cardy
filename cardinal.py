import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the game window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Cardinal Crossing")

# Load assets
cardinal_left = pygame.image.load("cardinal-left.png")
cardinal_right = pygame.image.load("cardinal-right.png")
log_img = pygame.image.load("log.png")
water_img = pygame.image.load("water.png")  # Now a 32x32 tile
water_top_img = pygame.image.load("water-top.png")  # New 32x32 tile for the dividing line
road_img_top = pygame.image.load("road-top.png")  # New 32x32 tile for the dividing line
road_img_bottom = pygame.image.load("road-bottom.png")  # New 32x32 tile for the dividing line

# Load new background and goal assets
try:
    grass_img = pygame.image.load("grass.png")  # Grass tile for background
    truck_img_right = pygame.image.load("truck-right.png")  # Grass tile for background
    truck_img_left = pygame.image.load("truck-left.png")  # Grass tile for background
    platform_img = pygame.image.load("platform.png")  # Platform for starting area
    goal_img = pygame.image.load("goal.png")  # Goal area (e.g., a tree or building)
except FileNotFoundError:
    print("Warning: Some assets not found. Please extract grass.png, truck.png, platform.png, and goal.png from the tileset.")
    grass_img = None
    truck_img_right = None
    truck_img_left = None
    platform_img = None
    goal_img = None

# Load background music
pygame.mixer.music.load("frogcave.ogg")
pygame.mixer.music.play(-1)  # Play background music on loop

# Scale images if needed
cardinal_left = pygame.transform.scale(cardinal_left, (32, 32))
cardinal_right = pygame.transform.scale(cardinal_right, (32, 32))
log_img = pygame.transform.scale(log_img, (100, 32))  # Scale log
water_img = pygame.transform.scale(water_img, (32, 32))  # Ensure water tile is 32x32
water_top_img = pygame.transform.scale(water_top_img, (32, 32))  # Ensure water-top tile is 32x32
truck_img_right = pygame.transform.scale(truck_img_right, (64, 32))  # Ensure water-top tile is 32x32
truck_img_left = pygame.transform.scale(truck_img_left, (64, 32))  # Ensure water-top tile is 32x32
road_img_top = pygame.transform.scale(road_img_top, (128, 64))  # Ensure water-top tile is 32x32
road_img_bottom = pygame.transform.scale(road_img_bottom, (128, 64))  # Ensure water-top tile is 32x32

# Scale Slates assets if they exist
if grass_img:
    grass_img = pygame.transform.scale(grass_img, (32, 32))  # Assuming 32x32 tiles
if truck_img_right:
    truck_img_right = pygame.transform.scale(truck_img_right, (64, 32))  # Assuming 64x32 trucks
if truck_img_left:
    truck_img_left = pygame.transform.scale(truck_img_left, (64, 32))  # Assuming 64x32 trucks
if road_img_top:
    road_img_top = pygame.transform.scale(road_img_top, (128, 64))  # Assuming 64x32 roads
if road_img_bottom:
    road_img_bottom = pygame.transform.scale(road_img_bottom, (128, 64))  # Assuming 64x32 roads
if platform_img:
    platform_img = pygame.transform.scale(platform_img, (80, 40))  # Platform for cardinal to start on
if goal_img:
    goal_img = pygame.transform.scale(goal_img, (32, 32))  # Goal area

# Colors
LIGHT_GREEN = (144, 238, 144)  # Light green for background
DARK_GREY = (50, 50, 50)  # Highway color
YELLOW = (255, 255, 0)  # Yellow lines

# Cardinal properties
cardinal = cardinal_right  # Default direction
cardinal_rect = cardinal.get_rect()
cardinal_rect.x = WINDOW_WIDTH // 2
cardinal_rect.y = 520  # Start just below the river section

# River section (y=300 to y=500)
RIVER_TOP = 300
RIVER_BOTTOM = 500

# Log properties
logs = []
for i in range(6):  # Create 6 logs
    log_rect = log_img.get_rect()
    log_rect.x = random.randint(0, WINDOW_WIDTH - log_rect.width)
    log_rect.y = RIVER_TOP + 20 + i * 32 + 5  # Space logs vertically in the river
    is_even = -1
    if i % 2 == 0:
        is_even = 1
    logs.append({"rect": log_rect, "speed": is_even * random.choice([1, 2])})  # Random direction

# Truck properties (highway at y=0 to y=300)
trucks = []
for i in range(4):  # Create 6 trucks
    truck_rect = truck_img_right.get_rect()  # Simple truck shape
    truck_rect.y = 64 + i * 32
    truck_rect.x = 0
    is_even = -1
    if i % 2 == 0:
        is_even = 1
    trucks.append({"rect": truck_rect, "speed": is_even * random.choice([1, 5]), "is_even" : is_even})

# Goal area (at the top of the highway)
goal_rect = pygame.Rect(WINDOW_WIDTH // 2 - 20, 10, 40, 40)  # Position at the top center

# Game variables
game_over = False
on_log = False
game_won = False

# Game loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                cardinal = cardinal_left
                cardinal_rect.x -= 32
            elif event.key == pygame.K_RIGHT:
                cardinal = cardinal_right
                cardinal_rect.x += 32
            elif event.key == pygame.K_UP:
                cardinal_rect.y -= 32
            elif event.key == pygame.K_DOWN:
                cardinal_rect.y += 32

    # Update logs
    on_log = False
    for log in logs:
        log["rect"].x += log["speed"]
        if log["rect"].x > WINDOW_WIDTH:
            log["rect"].x = -log["rect"].width
        elif log["rect"].x < -log["rect"].width:
            log["rect"].x = WINDOW_WIDTH
        # Check if cardinal is on a log (with a slightly expanded hitbox for forgiveness)
        log_hitbox = log["rect"]  # Expand hitbox by 10 pixels on each side
        if cardinal_rect.colliderect(log_hitbox) and RIVER_TOP <= cardinal_rect.y <= RIVER_BOTTOM:
            on_log = True
            cardinal_rect.x += log["speed"]  # Move with the log

    # Update trucks
    for truck in trucks:
        truck["rect"].x += truck["speed"]
        if truck["rect"].x > WINDOW_WIDTH:
            truck["rect"].x = -truck["rect"].width
        elif truck["rect"].x < -truck["rect"].width:
            truck["rect"].x = WINDOW_WIDTH
        # Check for collision with trucks
        if cardinal_rect.colliderect(truck["rect"]):
            game_over = True

    # Check if cardinal falls into water
    if RIVER_TOP <= cardinal_rect.y <= RIVER_BOTTOM and not on_log:
        print(f"Game Over: Cardinal at y={cardinal_rect.y}, on_log={on_log}")
        game_over = True

    # Check if cardinal reaches the goal
    if cardinal_rect.colliderect(goal_rect):
        game_won = True

    # Keep cardinal within bounds
    cardinal_rect.clamp_ip(window.get_rect())

    # Draw everything
    window.fill(LIGHT_GREEN)  # Clear screen with light green background

    # Draw grass background (top and bottom sections)
    if grass_img:
        for x in range(0, WINDOW_WIDTH, 32):
            for y in range(0, RIVER_TOP, 32):  # Top section (above river)
                window.blit(grass_img, (x, y))
            for y in range(RIVER_BOTTOM+32, WINDOW_HEIGHT, 32):  # Bottom section (below river)
                window.blit(grass_img, (x, y))
    else:
        # Fallback if grass.png is not available
        pygame.draw.rect(window, (0, 128, 0), (0, 0, WINDOW_WIDTH, RIVER_TOP))  # Green for top
        pygame.draw.rect(window, (0, 128, 0), (0, RIVER_BOTTOM, WINDOW_WIDTH, WINDOW_HEIGHT - RIVER_BOTTOM))  # Green for bottom

    # Draw highway (y=0 to y=300)
    #pygame.draw.rect(window, DARK_GREY, (0, 0, WINDOW_WIDTH, 300))
    for x in range(0, WINDOW_WIDTH, 128):
        window.blit(road_img_top, (x,64))
    #for x in range(0, WINDOW_WIDTH, 128):
    #    for y in range(0, RIVER_TOP, 128):
    #        window.blit(road_img_top, (x, y + 70))

    for x in range(0, WINDOW_WIDTH, 128):
        window.blit(road_img_bottom, (x, 128+16))

    # Draw water-top dividing line (at y=RIVER_TOP)
    for x in range(0, WINDOW_WIDTH, 32):
        window.blit(water_top_img, (x, RIVER_TOP))

    # Draw water (river section, y=300 to y=500)
    for x in range(0, WINDOW_WIDTH, 32):
        for y in range(RIVER_TOP+32, RIVER_BOTTOM, 32):
            window.blit(water_img, (x, y))

    # Draw logs
    for log in logs:
        window.blit(log_img, log["rect"])

    # Draw trucks
    for truck in trucks:
        if truck["is_even"] == -1:
            window.blit(truck_img_left, truck["rect"])
        else:
            window.blit(truck_img_right, truck["rect"])
        #pygame.draw.rect(window, (255, 0, 0), truck["rect"])  # Red trucks

    # Draw goal area
    if goal_img:
        window.blit(goal_img, goal_rect)
    else:
        pygame.draw.rect(window, (0, 255, 0), goal_rect)  # Green rectangle as placeholder

    # Draw starting platform
    if platform_img:
        window.blit(platform_img, (WINDOW_WIDTH // 2 - 40, 520))
    else:
        pygame.draw.rect(window, (150, 150, 150), (WINDOW_WIDTH // 2 - 40, 520, 80, 40))  # Grey rectangle as placeholder

    # Draw cardinal
    window.blit(cardinal, cardinal_rect)

    # Game over or win condition
    if game_over:
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over!", True, (255, 0, 0))
        window.blit(text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        break
    elif game_won:
        font = pygame.font.Font(None, 74)
        text = font.render("You Win!", True, (0, 255, 0))
        window.blit(text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        break

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
