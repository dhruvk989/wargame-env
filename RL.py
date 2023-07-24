import gym
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
from tqdm import tqdm
import os

# Import your custom environment
from env import DroneWargameEnv

# Create a function to make and wrap your environment
def make_env():
    def _init():
        env = DroneWargameEnv()
        return env
    return _init

# Create directories for saving models and TensorBoard logs
os.makedirs('models', exist_ok=True)
os.makedirs('tb_logs', exist_ok=True)

# Create the vectorized environment
env = DummyVecEnv([make_env()])

# Initialize the agent
model = PPO('CnnPolicy', env, verbose=1, tensorboard_log="./tb_logs/")

# Create a callback function to evaluate and save the model during training
eval_callback = EvalCallback(env, best_model_save_path='./models/',
                             log_path='./tb_logs/', eval_freq=500,
                             deterministic=True, render=False)

# Train the agent
print("Training starts...")
for _ in tqdm(range(1)):  # 10000 training steps
    model.learn(total_timesteps=10, callback=eval_callback)

# Save the final model
model.save("models/final_model")

# Load the best model
best_model = PPO.load("models/best_model")

# Evaluate the best model
mean_reward, std_reward = evaluate_policy(best_model, env, n_eval_episodes=10)

print(f"Best model's mean reward: {mean_reward}, std: {std_reward}")

print("Training completed.")

