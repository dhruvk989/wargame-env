import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Set up the display
display_info = pygame.display.Info()
display_width = display_info.current_w
display_height = display_info.current_h
display = pygame.display.set_mode(
    (display_width, display_height), pygame.FULLSCREEN)
pygame.display.set_caption("Drone Wargame")

# Load enemy and drone images
brick_image = pygame.image.load("brick.PNG")
enemy_image = pygame.image.load("enemy.png")
drone_image = pygame.image.load("drone.png")

# Resize the images
brick_width = 50
brick_height = 50
enemy_width = 50
enemy_height = 50
drone_width = 70
drone_height = 70
brick_image = pygame.transform.scale(brick_image, (brick_width, brick_height))
enemy_image = pygame.transform.scale(enemy_image, (enemy_width, enemy_height))
drone_image = pygame.transform.scale(drone_image, (drone_width, drone_height))

# Set up the drone
drone_x = display_width // 2 - drone_width // 2
drone_y = display_height - drone_height - 10
drone_speed = 0.0  # Initialize the drone speed to 0.0

# Set up the surveillance area points
surveillance_points = {
    'a': (200, 200),
    'b': (display_width - 200 - brick_width, 200),
    'c': (200, display_height - 200 - brick_height),
    'd': (display_width - 200 - brick_width, display_height - 200 - brick_height)
}
surveillance_points_reached = set()

# Set up enemies
num_enemies = 5
enemy_speed = 1
enemies = []
enemy_directions = []  # Store enemy movement directions
for _ in range(num_enemies):
    enemy_x = random.randint(
        brick_width, display_width - enemy_width - brick_width)
    enemy_y = random.randint(
        brick_height, display_height - enemy_height - brick_height)
    enemies.append((enemy_x, enemy_y))
    # Randomize the initial direction
    enemy_directions.append(random.choice([-1, 1]))

# Set up the font
font = pygame.font.Font(None, 36)

# Function to draw brick borders


def draw_brick_borders():
    for x in range(0, display_width, brick_width):
        display.blit(brick_image, (x, 0))
        display.blit(brick_image, (x, display_height - brick_height))
    for y in range(brick_height, display_height - brick_height, brick_height):
        display.blit(brick_image, (0, y))
        display.blit(brick_image, (display_width - brick_width, y))

# Function to draw surveillance area points


def draw_surveillance_points():
    for point, coordinates in surveillance_points.items():
        pygame.draw.rect(display, (255, 0, 0),
                         (*coordinates, brick_width, brick_height))

# Function to display speed


def display_speed(speed):
    speed_text = f"Speed: {speed:.2f} pixels/frame"
    text_surface = font.render(speed_text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(bottomright=(
        display_width - brick_width, display_height - brick_height))
    display.blit(text_surface, text_rect)

# Function to check if all surveillance points are reached


def check_surveillance_points():
    if surveillance_points_reached == set(surveillance_points.keys()):
        return True
    return False


# Main game loop
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Handle keyboard events
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and drone_x > brick_width:
        drone_x -= 5
    if keys[pygame.K_RIGHT] and drone_x < display_width - drone_width - brick_width:
        drone_x += 5
    if keys[pygame.K_UP] and drone_y > brick_height:
        drone_y -= 5
    if keys[pygame.K_DOWN] and drone_y < display_height - drone_height - brick_height:
        drone_y += 5

    # Update the drone speed based on the arrow keys
    if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
        drone_speed = 5.0
    else:
        drone_speed = 0.0

    # Clear the display
    display.fill((0, 0, 0))

    # Draw brick borders
    draw_brick_borders()

    # Draw the drone
    display.blit(drone_image, (drone_x, drone_y))

    # Move and draw the enemies
    for i in range(num_enemies):
        enemy_x, enemy_y = enemies[i]
        enemy_direction = enemy_directions[i]

        # Keep enemies within the brick borders
        if enemy_x <= brick_width or enemy_x >= display_width - enemy_width - brick_width:
            enemy_direction *= -1
        if enemy_y <= brick_height or enemy_y >= display_height - enemy_height - brick_height:
            enemy_direction *= -1

        enemy_x += enemy_direction * enemy_speed
        enemy_y += enemy_direction * enemy_speed

        display.blit(enemy_image, (enemy_x, enemy_y))
        enemies[i] = (enemy_x, enemy_y)
        enemy_directions[i] = enemy_direction

        # Check for collision with the drone
        if (
            drone_x < enemy_x + enemy_width and
            drone_x + drone_width > enemy_x and
            drone_y < enemy_y + enemy_height and
            drone_y + drone_height > enemy_y
        ):
            # Handle collision with the enemy (game over condition)
            print("Game Over!")
            pygame.quit()
            sys.exit()

    # Check if the drone has reached a surveillance point
    for point, coordinates in surveillance_points.items():
        if (
            drone_x >= coordinates[0] and
            drone_x <= coordinates[0] + brick_width and
            drone_y >= coordinates[1] and
            drone_y <= coordinates[1] + brick_height
        ):
            if point not in surveillance_points_reached:
                surveillance_points_reached.add(point)
                print(f"Surveillance of Point {point.upper()} Done!")

    # Check if all surveillance points are reached
    if check_surveillance_points():
        print("Surveillance Done! Game Won!")
        pygame.quit()
        sys.exit()

    # Display speed
    display_speed(drone_speed)

    # Draw surveillance area points
    draw_surveillance_points()

    # Update the display
    pygame.display.update()
    clock.tick(30)
