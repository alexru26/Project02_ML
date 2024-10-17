import sys

import pygame as pygame

from scenes.game.Game import Game
from scenes.menu.Menu import Menu

from sb3_contrib import RecurrentPPO

from src.Controls import Controls


class App:
    def __init__(self):
        self.model = RecurrentPPO.load('../models/ai')

        self.screen_width = 600
        self.screen_height = 900
        pygame.init()
        pygame.display.set_caption("TETRIS")
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.scene = None
        self.start_menu()

    def run(self):
        while True:
            # MY CODE #
            if isinstance(self.scene, Menu) or self.scene.game_over is True:
                events = pygame.event.get()
            elif isinstance(self.scene, Game):
                observation = self.scene.get_observation()
                actions, _states = self.model.predict(observation)
                events = []
                for action in actions:
                    if action == 0:
                        events.append(pygame.event.Event(pygame.KEYDOWN, key=Controls.move_left))
                    elif action == 1:
                        events.append(pygame.event.Event(pygame.KEYDOWN, key=Controls.move_right))
                    elif action == 2:
                        events.append(pygame.event.Event(pygame.KEYDOWN, key=Controls.soft_drop))
                    elif action == 3:
                        events.append(pygame.event.Event(pygame.KEYDOWN, key=Controls.rotate_cw))
                    elif action == 4:
                        events.append(pygame.event.Event(pygame.KEYDOWN, key=Controls.rotate_ccw))
                    elif action == 5:
                        events.append(pygame.event.Event(pygame.KEYDOWN, key=Controls.hard_drop))
                    elif action == 6:
                        events.append(pygame.event.Event(pygame.KEYDOWN, key=Controls.hold))
            # MY CODE #

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

