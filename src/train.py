import cv2
import gymnasium as gym
import torch
from pyglet import model
from sb3_contrib import RecurrentPPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.evaluation import evaluate_policy
from tetris_gymnasium.envs import Tetris

# create environment
env = gym.make("tetris_gymnasium/Tetris", render_mode="human")

def load_model(model_type):
    """
    Load the model
    :param model_type: new for creating a new model and load for loading a pretrained model
    :return: the model created
    """
    if model_type == 'new':
        policy_kwargs = dict(
            net_arch=dict(pi=[64, 64], vf=[64, 64]), # define network architecture
            activation_fn=torch.nn.Tanh, # define activation function
            lstm_hidden_size=256 # define lstm hidden size
        )

        model = RecurrentPPO(
            policy="MultiInputLstmPolicy", # policy for environment
            env=env, # environment
            policy_kwargs=policy_kwargs, # arguments defined above
            ent_coef=0.01, #
            n_steps=128, #
            batch_size=64, #
            gamma=0.99, #
            gae_lambda=0.95, #
            learning_rate=3e-4, #
            clip_range=0.2, #
            verbose=0 # don't log anything
        )
    elif model_type == 'load':
        # load model from models folder
        model = RecurrentPPO.load('../models/ai', env=env)
    else:
        # if model_type is not valid
        raise Exception('Invalid model type input')

    return model

def learn(timesteps):
    """
    Get the model to learn
    :param timesteps: how many timesteps to learn
    """
    eval_callback = EvalCallback(
        eval_env=env, # environment
        eval_freq=5000, # how often the performance is evaluated
        log_path='../logs' # log path
    )

    model.learn(total_timesteps=int(timesteps), callback=eval_callback)

    # save the model, which is pretty important
    model.save('../models/ai')

def test():
    """
    Test the model in the gym environment
    """
    vec_env = model.get_env()
    observation = vec_env.reset()
    for i in range(10):
        terminated = False
        while not terminated:
            vec_env.render()
            action, _states = model.predict(observation)
            observation, reward, terminated, info = vec_env.step(action)
            key = cv2.waitKey(60)

def evaluate(episodes):
    """
    Evaluate the performance of the model after 10 episodes
    """
    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=episodes)
    # print average reward and standard deviation
    print(f'Mean reward: {mean_reward} +- {std_reward}')

if __name__ == '__main__':
    model = load_model(model_type='load')
    #learn(timesteps=2e6)
    #test()
    evaluate(episodes=100)
    env.close()
