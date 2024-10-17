import cv2
import torch
import gymnasium as gym
from sb3_contrib import RecurrentPPO
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.callbacks import EvalCallback
from tetris_gymnasium.envs.tetris import Tetris

env = gym.make("tetris_gymnasium/Tetris", render_mode="human")

policy_kwargs = dict(
    net_arch=dict(pi=[64, 64], vf=[64, 64]),
    activation_fn=torch.nn.Tanh,
    lstm_hidden_size=256
)

# model = RecurrentPPO(
#     policy="MultiInputLstmPolicy",
#     env=env,
#     policy_kwargs=policy_kwargs,
#     ent_coef=0.01,
#     n_steps=128,
#     batch_size=64,
#     gamma=0.99,
#     gae_lambda=0.95,
#     learning_rate=3e-4,
#     clip_range=0.2,
#     verbose=0
# )

model = RecurrentPPO.load('../models/ai', env=env)

eval_callback = EvalCallback(
    eval_env=env,
    eval_freq=1000,
    log_path='../logs'
)

# model.learn(total_timesteps=int(2e6), callback=eval_callback)

vec_env = model.get_env()
observation = vec_env.reset()
for i in range(10):
    terminated = False
    while not terminated:
        vec_env.render()
        action, _states = model.predict(observation)
        observation, reward, terminated, info = vec_env.step(action)
        key = cv2.waitKey(60)

model.save('../models/ai')

mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=10)
print(f'Mean reward: {mean_reward} +- {std_reward}')

env.close()
