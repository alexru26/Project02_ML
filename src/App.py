import os
import sys

import pygame as pygame

from scenes.game.Game import Game
from scenes.menu.Menu import Menu

from sb3_contrib import RecurrentPPO

from src.Controls import Controls


class App:
    def __init__(self):
        while True:  # choose model to load
            name = input('Model name: ')
            if os.path.isfile('../models/' + name + '.zip'):
                self.model = RecurrentPPO.load('../models/' + name)
                break

        self.screen_width = 600
        self.screen_height = 900
        pygame.init()
        pygame.display.set_caption("TETRIS")
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.scene = None
        self.start_menu()

    def run(self):
        move_made = False # track if move was made
        when_move_made = pygame.time.get_ticks() # track when the move was made
        delay = 200 # delay between each move

        left_pressed = False # track if left was pressed
        right_pressed = False # track if right was pressed
        soft_drop_pressed = False # track if soft drop was pressed
        while True:
            events = []
            current_time = pygame.time.get_ticks()

            if current_time >= when_move_made + delay: # if current time has exceeded delay
                move_made = False

            if left_pressed: # if left was just pressed, stop pressing left
                events.append(pygame.event.Event(pygame.KEYUP, key=Controls.move_left))
                left_pressed = False

            if right_pressed: # if right was just pressed, stop pressing right
                events.append(pygame.event.Event(pygame.KEYUP, key=Controls.move_right))
                right_pressed = False

            if soft_drop_pressed: # if soft drop was just pressed, stop pressing soft drop
                events.append(pygame.event.Event(pygame.KEYUP, key=Controls.soft_drop))
                soft_drop_pressed = False

            if isinstance(self.scene, Menu) or self.scene.game_over: # if in Menu or game over
                events.extend(pygame.event.get())
            elif isinstance(self.scene, Game) and not move_made: # if in game screen, meaning AI input
                observation = self.scene.get_observation() # get observation
                actions, _states = self.model.predict(observation) # predict based on observation
                for action in actions: # loop through actions and append to events accordingly
                    if action == 0: # left
                        left_pressed = True
                        events.append(pygame.event.Event(pygame.KEYDOWN, key=Controls.move_left))
                    elif action == 1: # right
                        right_pressed = True
                        events.append(pygame.event.Event(pygame.KEYDOWN, key=Controls.move_right))
                    elif action == 2: # soft drop
                        soft_drop_pressed = True
                        events.append(pygame.event.Event(pygame.KEYDOWN, key=Controls.soft_drop))
                    elif action == 3: # rotate clockwise
                        events.append(pygame.event.Event(pygame.KEYDOWN, key=Controls.rotate_cw))
                    elif action == 4: # rotate counterclockwise
                        events.append(pygame.event.Event(pygame.KEYDOWN, key=Controls.rotate_ccw))
                    elif action == 5: # hard drop
                        events.append(pygame.event.Event(pygame.KEYDOWN, key=Controls.hard_drop))
                    elif action == 6: # hold
                        events.append(pygame.event.Event(pygame.KEYDOWN, key=Controls.hold))

                move_made = True
                when_move_made = current_time

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # update
            self.scene.update(events)

            # draw
            self.screen.fill("black")
            self.scene.draw()
            pygame.display.flip()

            self.clock.tick(60)

    def start_game(self):
        self.scene = Game(self, self.screen)

    def start_menu(self):
        self.scene = Menu(self, self.screen)

