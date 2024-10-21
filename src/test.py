import cv2
import gymnasium as gym
from tetris_gymnasium.envs import Tetris

if __name__ == "__main__":
    # create environment
    env = gym.make("tetris_gymnasium/Tetris", render_mode="human")

    # set seed to make testing easier
    seed = 1
    env.reset(seed=seed)

    terminated = False
    while not terminated: # while game is still going
        env.render() # render it
        action = None
        while action is None: # wait until some action
            key = cv2.waitKey(1)

            if key == ord("a"):
                action = env.unwrapped.actions.move_left
            elif key == ord("d"):
                action = env.unwrapped.actions.move_right
            elif key == ord("s"):
                action = env.unwrapped.actions.move_down
            elif key == ord("w"):
                action = env.unwrapped.actions.rotate_counterclockwise
            elif key == ord("e"):
                action = env.unwrapped.actions.rotate_clockwise
            elif key == ord(" "):
                action = env.unwrapped.actions.hard_drop
            elif key == ord("q"):
                action = env.unwrapped.actions.swap
            elif key == ord("r"):
                env.reset(seed=seed)
                break

        observation, reward, terminated, truncated, info = env.step(action) # action is taken in environment
        print(observation['board']) # debug stuff
        print(observation['active_tetromino_mask']) # debug stuff
        print()

    print("Game Over!")