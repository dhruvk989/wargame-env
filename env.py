import gym
from gym import spaces
import numpy as np
import pygame
import random
import re


class DroneWargameEnv(gym.Env):
    def __init__(self):
        super(DroneWargameEnv, self).__init__()

        # Initialize Pygame
        pygame.init()

        # Set up the display
        display_info = pygame.display.Info()
        self.display_width = display_info.current_w
        self.display_height = display_info.current_h
        self.display = pygame.display.set_mode((self.display_width, self.display_height))

        # Define action and observation space
        self.action_space = spaces.Discrete(4)  # up, down, left, right
        self.observation_space = spaces.Box(low=0, high=255, shape=(80, 80, 3), dtype=np.uint8)

        # Define other attributes
        self.drone_speed = 10
        self.enemy_speed = 5
        self.enemy_range = 100
        self.drone_range = 50
        self.start_time = None
        self.game_time = 60

        # Define drone dimensions
        self.drone_width = 10
        self.drone_height = 10

        # Define enemy dimensions
        self.enemy_width = 10
        self.enemy_height = 10

        # Define number of enemies
        self.num_enemies = 5

        # Define surveillance points
        self.num_points = 5

        # Define box dimensions
        self.box_x = 0
        self.box_y = 0
        self.box_width = self.display_width
        self.box_height = self.display_height

        # Define reward dimensions
        self.reward_width = 10
        self.reward_height = 10

        # Initialize drone and enemies
        self.reset()

    def calculate_distance(self, x1, y1, x2, y2):
        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

    def get_state(self):
        # Create an empty image
        state = np.zeros((80, 80, 3), dtype=np.uint8)

        # Draw the drone
        state[self.drone_y:self.drone_y+10, self.drone_x:self.drone_x+10] = [0, 255, 0]

        # Draw the enemies
        for enemy in self.enemies:
            state[enemy[1]:enemy[1]+10, enemy[0]:enemy[0]+10] = [255, 0, 0]

        # Draw the surveillance points
        for point in self.surveillance_points.values():
            state[point[1]:point[1]+10, point[0]:point[0]+10] = [0, 0, 255]

        return state

    def step(self, action):
        # Define the reward
        reward = 0

        # Define the done flag
        done = False

        # Move the drone based on the action
        if action == 0 and self.drone_y > 0:  # up
            self.drone_y -= self.drone_speed
        elif action == 1 and self.drone_y < self.display_height - self.drone_height:  # down
            self.drone_y += self.drone_speed
        elif action == 2 and self.drone_x > 0:  # left
            self.drone_x -= self.drone_speed
        elif action == 3 and self.drone_x < self.display_width - self.drone_width:  # right
            self.drone_x += self.drone_speed

        # Check if the drone is inside the surveillance box
        if self.box_x <= self.drone_x <= self.box_x + self.box_width and self.box_y <= self.drone_y <= self.box_y + self.box_height:
            reward = 1

        # Move enemies
        for enemy in self.enemies:
            direction = random.choice(['up', 'down', 'left', 'right'])
            if direction == 'up' and enemy[1] > 0:
                enemy[1] -= self.enemy_speed
            elif direction == 'down' and enemy[1] < self.display_height - self.enemy_height:
                enemy[1] += self.enemy_speed
            elif direction == 'left' and enemy[0] > 0:
                enemy[0] -= self.enemy_speed
            elif direction == 'right' and enemy[0] < self.display_width - self.enemy_width:
                enemy[0] += self.enemy_speed

            # Check if the enemy has detected the drone
            if self.calculate_distance(self.drone_x, self.drone_y, enemy[0], enemy[1]) <= self.enemy_range:
                done = True
                reward = -1

        return self.get_state(), reward, done, {}

    def reset(self, _seed=None):
        # Reset the drone position
        self.drone_x = self.display_width // 2 - self.drone_width // 2
        self.drone_y = self.display_height - self.drone_height - 10

        # Reset the enemies
        self.enemies = [[random.randint(0, self.display_width - self.enemy_width), random.randint(
            0, self.display_height - self.enemy_height - 200)] for _ in range(self.num_enemies)]

        # Reset the surveillance points
        self.surveillance_points = {f'p{i}': (random.randint(self.box_x, self.box_x + self.box_width - self.reward_width), random.randint(
            self.box_y, self.box_y + self.box_height - self.reward_height)) for i in range(self.num_points)}

        # Reset the set of reached surveillance points
        self.surveillance_points_reached = set()

        # Reset the start time
        self.start_time = pygame.time.get_ticks()

        # Return the initial state
        return self.get_state()

    def render(self, mode='human'):
        # Clear the screen
        self.display.fill((0, 0, 0))

        # Draw the drone
        pygame.draw.circle(self.display, (0, 255, 0), (self.drone_x, self.drone_y), 10)

        # Draw the enemies
        for enemy in self.enemies:
            pygame.draw.circle(self.display, (255, 0, 0), (enemy[0], enemy[1]), 10)

        pygame.display.flip()

    def close(self):
        pygame.quit()
