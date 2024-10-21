# Machine Learning Project 02: Tetris AI
This is an AI that is pretty bad at Tetris.

## How to run
Make sure you have the necessary packages.

```
pip install pandas
pip install torch
pip install gym
pip install gymnasium
pip install stable-baselines3
pip install tetris-gymnasium
```

Run main.py to play against the AI.

## Resources Used
- https://github.com/Max-We/Tetris-Gymnasium
- https://github.com/vonkez/Tetris-pygame
- https://stable-baselines3.readthedocs.io/en/master/index.html
- https://huggingface.co/learn/deep-rl-course/
- ChatGPT

## How it works
- Model is a Recurrent PPO model
- Model is trained in gym environment through reinforcement learning
- Model is fed dictionary
  - ```board```: the board that includes pieces and active piece
  - ```active_tetromino_mask```: location of active piece, represented by square
  - ```holder```: piece in hold
  - ```queue```: next four pieces
- Model returns integer, which represents move
- Model is applied to pygame

<img width="630" alt="Screenshot 2024-10-21 at 4 21 41 PM" src="https://github.com/user-attachments/assets/87911534-39aa-4f6d-8c44-3a3874691cc8">

*Image 1. Model parameters.*

## Reasoning and Issues
- 0th attempt: DQN model
  - Training time is quick, but improving slowly
- 1st attempt: ```ai.zip```
  - Recurrent PPO model, which uses LSTM 
  - Not exploring enough
    - Low entropy coefficient
    - Always just spamming hard drop in the middle
  - Not complex enough
- 2nd attempt: ```aiv2.zip```
  - Increased entropy coefficient
    - Trying a lot
    - Will take a lot of time to get good
  - Does worse than previous model
  - Takes longer because more complex

## Further Improvements
- Train for more
  - Since my model is kinda random, it'll take a very long time for it to get very good
- Further investigate gym vs pygame differences
  - Model performs differently between two environments
- Not use reinforcement learning
  - Maybe using minimax and board analysis?
