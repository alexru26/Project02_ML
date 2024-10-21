import cv2
import gymnasium as gym
import os.path
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
            net_arch=dict(pi=[128, 128], vf=[128, 128]), # define network architecture
            activation_fn=torch.nn.Tanh, # define activation function
            lstm_hidden_size=512 # define lstm hidden size
        )

        model = RecurrentPPO(
            policy="MultiInputLstmPolicy", # policy for environment
            env=env, # environment
            policy_kwargs=policy_kwargs, # arguments defined above
            ent_coef=0.02, #
            n_steps=2048, #
            batch_size=128, #
            gamma=0.99, # discount factor (dictates long-term vs short-term benefits)
            gae_lambda=0.95, #
            learning_rate=3e-4, # how fast it learns/changes
            clip_range=0.2, #
            verbose=0 # don't log anything
        )
    elif model_type == 'load':
        # load model from models folder
        while True: # choose model to load
            name = input('Model name: ')
            if os.path.isfile('../models/'+name+'.zip'):
                model = RecurrentPPO.load('../models/'+name, env=env)
                break
    else:
        # if model_type is not valid
        raise Exception('Invalid model type input')

    return model

def learn(timesteps, name, eval_freq, verbose):
    """
    Get the model to learn
    :param timesteps: how many timesteps to learn
    :param name: name of the model
    :param eval_freq: how often to evaluate the model
    :param verbose: log or not
    """
    if verbose == 1: # if I want to log how it is doing
        eval_callback = EvalCallback(
            eval_env=env, # environment
            eval_freq=int(eval_freq), # how often the performance is evaluated
            log_path='../logs' # log path
        )
    else: # if I don't want to log how it is doing
        eval_callback = None

    # learn!!!
    model.learn(total_timesteps=int(timesteps), callback=eval_callback)

    # save the model, which is pretty important
    model.save('../models/'+name)

def test(games):
    """
    Test the model in the gym environment
    """
    vec_env = model.get_env() # create demo environment
    observation = vec_env.reset() # reset it
    for i in range(games): # number of times to simulate game
        terminated = False
        while not terminated: # this while represents 1 game
            vec_env.render() # render it
            action, _states = model.predict(observation) # model makes a prediction based on observation
            observation, reward, terminated, info = vec_env.step(action) # action is taken in environment, returns another observation
            key = cv2.waitKey(60) # delay between each move

def evaluate(episodes):
    """
    Evaluate the performance of the model after 10 episodes
    """
    # evaluate how well the model is doing based on episodes
    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=episodes)
    # print average reward and standard deviation
    print(f'Mean reward: {mean_reward} +- {std_reward}')

if __name__ == '__main__':
    model = load_model(model_type='load')
    print('Start training!\n')
    # for i in range(10):
    #     learn(timesteps=1e5, name='aiv2', eval_freq=2e4, verbose=1)
    #     evaluate(episodes=100)
    #     print()
    #test(games=10)
    #evaluate(episodes=100)
    env.close()
