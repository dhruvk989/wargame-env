import pygame_gui
import random
import sys
import pygame

# Initialize Pygame
pygame.init()


# Set up the display
display_info = pygame.display.Info()
display_width = display_info.current_w
display_height = display_info.current_h
display = pygame.display.set_mode(
    (display_width, display_height), pygame.FULLSCREEN)
pygame.display.set_caption("Drone Wargame")

# Load the background image
bg_image = pygame.image.load("dhr/bg.jpg")
bg_image = pygame.transform.scale(bg_image, (display_width, display_height))

# Load images
enemy_image = pygame.image.load("soldier.png")
drone_image = pygame.image.load("drone.png")
reward_image = pygame.image.load("reward.png")

# Resize the images
enemy_width = 50
enemy_height = 50
drone_width = 70
drone_height = 70
reward_width = 30
reward_height = 30
enemy_image = pygame.transform.scale(enemy_image, (enemy_width, enemy_height))
drone_image = pygame.transform.scale(drone_image, (drone_width, drone_height))
reward_image = pygame.transform.scale(
    reward_image, (reward_width, reward_height))

# Set up the drone
drone_x = display_width // 2 - drone_width // 2
drone_y = display_height - drone_height - 10
drone_path = []

# Set up GUI manager
manager = pygame_gui.UIManager((display_width, display_height))

# Create GUI elements
num_points_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((display_width//2, 50), (100, 50)), manager=manager)
num_enemies_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((display_width//2, 100), (100, 50)), manager=manager)
enemy_speed_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((display_width//2, 150), (100, 50)), manager=manager)
enemy_range_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((display_width//2, 200), (100, 50)), manager=manager)
drone_speed_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((display_width//2, 250), (100, 50)), manager=manager)
drone_range_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((display_width//2, 300), (100, 50)), manager=manager)
time_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((display_width//2, 350), (100, 50)), manager=manager)
box_x_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((display_width//2, 400), (100, 50)), manager=manager)
box_y_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((display_width//2, 450), (100, 50)), manager=manager)
box_width_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((display_width//2, 500), (100, 50)), manager=manager)
box_height_textbox = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((display_width//2, 550), (100, 50)), manager=manager)
start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
    (display_width//2, 600), (100, 50)), text='Start', manager=manager)

# Create labels
num_points_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (display_width//2 - 150, 50), (150, 50)), text='Number of Points:', manager=manager)
num_enemies_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (display_width//2 - 150, 100), (150, 50)), text='Number of Enemies:', manager=manager)
enemy_speed_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (display_width//2 - 150, 150), (150, 50)), text='Enemy Speed:', manager=manager)
enemy_range_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (display_width//2 - 150, 200), (150, 50)), text='Enemy Range:', manager=manager)
drone_speed_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (display_width//2 - 150, 250), (150, 50)), text='Drone Speed:', manager=manager)
drone_range_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (display_width//2 - 150, 300), (150, 50)), text='Drone Range:', manager=manager)
time_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (display_width//2 - 150, 350), (150, 50)), text='Game Time:', manager=manager)
box_x_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (display_width//2 - 150, 400), (150, 50)), text='Box X:', manager=manager)
box_y_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (display_width//2 - 150, 450), (150, 50)), text='Box Y:', manager=manager)
box_width_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (display_width//2 - 150, 500), (150, 50)), text='Box Width:', manager=manager)
box_height_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(
    (display_width//2 - 150, 550), (150, 50)), text='Box Height:', manager=manager)

# Create enemies
num_enemies = 5
enemy_speed = 2
enemies = []

# Set up the surveillance points
num_points = 4
surveillance_points = {}
surveillance_points_reached = set()

# Define the surveillance box
box_x = 100
box_y = 100
box_width = display_width - 200
box_height = display_height - 200

# Function to calculate the distance between two points
def calculate_distance(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

def calculate_direction(current_x, current_y, target_x, target_y, enemies, safe_distance):
    dx = target_x - current_x
    dy = target_y - current_y

    for enemy in enemies:
        enemy_x, enemy_y = enemy
        distance_to_enemy = calculate_distance(current_x, current_y, enemy_x, enemy_y)
        if distance_to_enemy < safe_distance:
            dx -= (enemy_x - current_x)
            dy -= (enemy_y - current_y)

    return dx, dy

def mindset(drone_x, drone_y, surveillance_points, surveillance_points_reached, enemies, enemy_range):
    # Choose the closest surveillance point that hasn't been reached yet as the new target
    remaining_points = {point: coordinates for point, coordinates in surveillance_points.items() if point not in surveillance_points_reached}
    target = min(remaining_points, key=lambda point: calculate_distance(drone_x, drone_y, *remaining_points[point]))

    # Calculate the direction to move in
    dx, dy = calculate_direction(drone_x, drone_y, *remaining_points[target], enemies, enemy_range)

    # Normalize the direction and multiply by the drone speed
    length = (dx**2 + dy**2)**0.5
    dx = (dx / length) * drone_speed
    dy = (dy / length) * drone_speed

    # Return the new position for the drone
    return [(drone_x + dx, drone_y + dy)]



# Main game loop
running = True
clock = pygame.time.Clock()
start_time = None
game_time = 0
drone_speed = 0
drone_range = 0
enemy_range = 0
game_started = False
while running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == start_button:
                    num_points = int(num_points_textbox.get_text())
                    num_enemies = int(num_enemies_textbox.get_text())
                    enemy_speed = int(enemy_speed_textbox.get_text())
                    enemy_range = int(enemy_range_textbox.get_text())
                    drone_speed = int(drone_speed_textbox.get_text())
                    drone_range = int(drone_range_textbox.get_text())
                    game_time = int(time_textbox.get_text())
                    box_x = int(box_x_textbox.get_text())
                    box_y = int(box_y_textbox.get_text())
                    box_width = int(box_width_textbox.get_text())
                    box_height = int(box_height_textbox.get_text())
                    start_time = pygame.time.get_ticks()
                    enemies = [[random.randint(0, display_width - enemy_width), random.randint(
                        0, display_height - enemy_height - 200)] for _ in range(num_enemies)]
                    surveillance_points = {f'p{i}': [random.randint(box_x, box_x + box_width - reward_width), random.randint(
                        box_y, box_y + box_height - reward_height)] for i in range(num_points)}
                    game_started = True
                    manager.clear_and_reset()

        manager.process_events(event)

    manager.update(time_delta)

    if game_started:
        if game_started:
        # If drone reached the current point, generate the next point
            if not drone_path or (drone_x, drone_y) == drone_path[-1]:
                drone_path = mindset(drone_x, drone_y, surveillance_points,
                                 surveillance_points_reached, enemies, enemy_range)
        # If there's a path, make the drone follow the path
            if drone_path:
                next_point = drone_path.pop(0)
                drone_x, drone_y = next_point
        # Move enemies
        for enemy in enemies:
            direction = random.choice(['up', 'down', 'left', 'right'])
            if direction == 'up' and enemy[1] > 0:
                enemy[1] -= enemy_speed
            elif direction == 'down' and enemy[1] < display_height - enemy_height:
                enemy[1] += enemy_speed
            elif direction == 'left' and enemy[0] > 0:
                enemy[0] -= enemy_speed
            elif direction == 'right' and enemy[0] < display_width - enemy_width:
                enemy[0] += enemy_speed

            # Check if the drone has detected an enemy
            if calculate_distance(drone_x, drone_y, enemy[0], enemy[1]) <= drone_range:
                print(f"Drone detected enemy at ({enemy[0]}, {enemy[1]})")

            # Check if the enemy has detected the drone
            if calculate_distance(enemy[0], enemy[1], drone_x, drone_y) <= enemy_range:
                print(
                    f"Game Over! Enemy detected drone at ({drone_x}, {drone_y})")
                running = False
                break

        # Check if the drone has reached a surveillance point
        for point, coordinates in surveillance_points.items():
            if calculate_distance(drone_x, drone_y, coordinates[0], coordinates[1]) <= drone_range:
                if point not in surveillance_points_reached:
                    surveillance_points_reached.add(point)
                    print(f"Surveillance of Point {point.upper()} Done!")

        # Check if all surveillance points are reached
        if len(surveillance_points_reached) == len(surveillance_points):
            print("Game Won! All surveillance points reached.")
            running = False

    # Draw everything
    display.blit(bg_image, (0, 0))  # Draw the background image
    display.blit(drone_image, (drone_x, drone_y))  # Draw the drone
    for enemy in enemies:
        display.blit(enemy_image, (enemy[0], enemy[1]))  # Draw the enemies

    # Draw surveillance points
    for point, coordinates in surveillance_points.items():
        if point not in surveillance_points_reached:
            display.blit(reward_image, coordinates)
    # Draw the surveillance box
    pygame.draw.rect(display, (0, 0, 0),
                 (box_x, box_y, box_width, box_height), 2)

   # Draw drone path
    if len(drone_path) > 1:
        pygame.draw.lines(display, (255, 0, 0), False, drone_path, 2)

    manager.draw_ui(display)

    # Display remaining time
    if start_time is not None:
        elapsed_time = (pygame.time.get_ticks() - start_time) / \
            1000  # convert milliseconds to seconds
        remaining_time = max(0, game_time - elapsed_time)
        time_text = f'Time left: {remaining_time:.2f}s'
        time_surface = pygame.font.Font(None, 36).render(
            time_text, True, (255, 255, 255))
        display.blit(time_surface, (display_width - 200, 10))

        if remaining_time <= 0:
            print("Game Over! Time's up.")
            running = False

    # Display drone and enemies coordinates
    drone_coordinates_text = f'Drone: ({drone_x}, {drone_y})'
    drone_coordinates_surface = pygame.font.Font(None, 24).render(
        drone_coordinates_text, True, (255, 255, 255))
    display.blit(drone_coordinates_surface, (10, 10))
    for i, enemy in enumerate(enemies):
        enemy_coordinates_text = f'Enemy {i+1}: ({enemy[0]}, {enemy[1]})'
        enemy_coordinates_surface = pygame.font.Font(None, 24).render(
            enemy_coordinates_text, True, (255, 255, 255))
        display.blit(enemy_coordinates_surface, (10, 40 + i*30))

    pygame.display.flip()

pygame.quit()
