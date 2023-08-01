import pygame
import pygame_gui
import random
import sys
import csv
import matplotlib.pyplot as plt

# Initialize Pygame
pygame.init()

# Set up the display
display_info = pygame.display.Info()
display_width = display_info.current_w
display_height = display_info.current_h
display = pygame.display.set_mode((display_width, display_height), pygame.FULLSCREEN)
pygame.display.set_caption("Drone Wargame")

# Load the background image
bg_image = pygame.image.load(r"C:\Users\dhruv kumar\Desktop\dhruv\dhr\bg.jpg")
bg_image = pygame.transform.scale(bg_image, (display_width, display_height))

# Load images
enemy_image = pygame.image.load("jet.png")
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
reward_image = pygame.transform.scale(reward_image, (reward_width, reward_height))

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
            # Increase the weight of closer enemies
            weight = safe_distance / distance_to_enemy
            dx -= weight * (enemy_x - current_x)
            dy -= weight * (enemy_y - current_y)

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

# Define the ranges for your parameters
ranges = {
    "num_points": (1, 5),
    "num_enemies": (1, 5),
    "enemy_speed": (1, 5),
    "enemy_range": (1, 5),
    "drone_speed": (1, 5),
    "drone_range": (1, 50),
    "game_time": (10, 60),
    "box_x": (350, 400),  # Adjusted range
    "box_y": (350,400),  # Adjusted range
    "box_width": (1000,1200),
    "box_height": (400, 600)
}

# Create a dataset with 50 entries
dataset = []
for _ in range(50):
    entry = {param: random.randint(*ranges[param]) for param in ranges}
    dataset.append(entry)

# Open the log file
reward_log = open('reward_log.csv', 'w', newline='')
reward_writer = csv.writer(reward_log)
reward_writer.writerow(['Time', 'Reward'])

successes = 0

for parameters in dataset:
    # Set up your inputs here...
    num_points = parameters["num_points"]
    num_enemies = parameters["num_enemies"]
    enemy_speed = parameters["enemy_speed"]
    enemy_range = parameters["enemy_range"]
    drone_speed = parameters["drone_speed"]
    drone_range = parameters["drone_range"]
    game_time = parameters["game_time"]
    box_x = parameters["box_x"]
    box_y = parameters["box_y"]
    box_width = parameters["box_width"]
    box_height = parameters["box_height"]

    # Set up the drone
    drone_x = display_width // 2 - drone_width // 2
    drone_y = display_height - drone_height - 10
    drone_path = []

    # Create enemies
    enemies = [[random.randint(0, display_width - enemy_width), random.randint(0, display_height - enemy_height - 200)] for _ in range(num_enemies)]

    # Set up the surveillance points
    surveillance_points = {f'p{i}': [random.randint(box_x, box_x + box_width - reward_width), random.randint(box_y, box_y + box_height - reward_height)] for i in range(num_points)}
    surveillance_points_reached = set()

    # Main game loop
    running = True
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    game_started = True
    rewards = 0
    in_box = False
    while running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if game_started:
            # If drone reached the current point, generate the next point
            if not drone_path or (drone_x, drone_y) == drone_path[-1]:
                drone_path = mindset(drone_x, drone_y, surveillance_points, surveillance_points_reached, enemies, enemy_range)
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
                    print(f"Game Over! Enemy detected drone at ({drone_x}, {drone_y})")
                    running = False
                    game_started = True
                    break

            # Check if the drone is in the surveillance box
            if box_x <= drone_x <= box_x + box_width and box_y <= drone_y <= box_y + box_height:
                if not in_box:
                    rewards += 10  # Reward for entering the surveillance box
                    in_box = True
            else:
                if in_box:
                    rewards -= 10  # Penalty for leaving the surveillance box
                    in_box = False

            # Check if the drone has reached a surveillance point
            for point, coordinates in surveillance_points.items():
                distance = calculate_distance(drone_x, drone_y, coordinates[0], coordinates[1])
                if distance <= drone_range:
                    if point not in surveillance_points_reached:
                        surveillance_points_reached.add(point)
                        rewards += 10  # Reward for completing a surveillance point
                        print(f"Surveillance of Point {point.upper()} Done!")

            # Check if all surveillance points are reached
            if len(surveillance_points_reached) == len(surveillance_points):
                print("Game Won! All surveillance points reached.")
                successes += 1
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
        pygame.draw.rect(display, (0, 0, 0), (box_x, box_y, box_width, box_height), 2)

        # Draw drone path
        if len(drone_path) > 1:
            pygame.draw.lines(display, (255, 0, 0), False, drone_path, 2)

        pygame.display.flip()

        # Display remaining time
        if start_time is not None:
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  # convert milliseconds to seconds
            remaining_time = max(0, game_time - elapsed_time)
            time_text = f'Time left: {remaining_time:.2f}s'
            time_surface = pygame.font.Font(None, 36).render(time_text, True, (255, 255, 255))
            display.blit(time_surface, (display_width - 200, 10))

            if remaining_time <= 0:
                print("Game Over! Time's up.")
                running = False

        # Log the current reward
        reward_writer.writerow([pygame.time.get_ticks() / 1000, rewards])  # Convert time to seconds

    # Reset the game state for the next game
    drone_x = display_width // 2 - drone_width // 2
    drone_y = display_height - drone_height - 10
    drone_path = []
    enemies = [[random.randint(0, display_width - enemy_width), random.randint(0, display_height - enemy_height - 200)] for _ in range(num_enemies)]
    surveillance_points = {f'p{i}': [random.randint(box_x, box_x + box_width - reward_width), random.randint(box_y, box_y + box_height - reward_height)] for i in range(num_points)}
    surveillance_points_reached = set()
    running = True
    start_time = pygame.time.get_ticks()
    game_started = True
    rewards = 0
    in_box = False

# Close the log file
reward_log.close()

# Load the rewards from the log file
rewards = []
times = []
with open('reward_log.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Skip the header
    for row in reader:
        times.append(float(row[0]))
        rewards.append(int(row[1]))

# Plot the rewards
plt.plot(times, rewards)
plt.xlabel('Time (s)')
plt.ylabel('Reward')
plt.title('Reward over time')
plt.show()

# Calculate success rate
success_rate = successes / len(dataset) * 100
print(f"Success rate: {success_rate}%")

pygame.quit()
