import cv2
import gymnasium as gym
from stable_baselines3 import PPO
from tetris_gymnasium.envs.tetris import Tetris

env = gym.make("tetris_gymnasium/Tetris", render_mode="human")

model = PPO("MultiInputPolicy", env, verbose=1)
model.learn(total_timesteps=int(1e5), progress_bar=True)

vec_env = model.get_env()
observation = vec_env.reset()
for i in range(10):
    terminated = False
    while not terminated:
        vec_env.render()
        action, _states = model.predict(observation, deterministic=True)
        observation, reward, terminated, info = vec_env.step(action)
        key = cv2.waitKey(100)
model.save('../models/ai')
env.close()
