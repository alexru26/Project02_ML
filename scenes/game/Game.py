import math
from typing import List

import pygame
from pygame.event import Event

import numpy as np

from src.Controls import Controls
from scenes.game.Block import Block
from scenes.game.Board import Board
from scenes.game.GameOverMenu import GameOverMenu
from scenes.game.HoldBox import HoldBox
from scenes.game.NextBlocks import NextBlocks
from scenes.game.PauseMenu import PauseMenu
from scenes.game.ScoreBoard import ScoreBoard


class Game:
    def __init__(self, app, screen):
        self.app = app
        self.screen = screen
        self.font = pygame.font.Font("../assets/PressStart2P-Regular.ttf", 32)
        self.gravity_levels = {
            1: 0.01667,
            2: 0.021017,
            3: 0.026977,
            4: 0.035256,
            5: 0.04693,
            6: 0.06361,
            7: 0.0879,
            8: 0.1236,
            9: 0.1775,
            10: 0.2598,
            11: 0.388,
            12: 0.59,
            13: 0.92,
            14: 1.46,
            15: 2.36,
        }

        # music
        pygame.mixer.music.load('../assets/soundtrack.mp3')
        pygame.mixer.music.set_volume(0.05)
        pygame.mixer.music.play(-1)

        # alt bölümler
        self.board = Board(self.screen, x=140, y=20, cell_size=32)
        self.hold_box = HoldBox(self.screen, x=4, y=84)
        self.next_blocks = NextBlocks(self.screen, self.board, x=460, y=84)
        self.active_block: Block = self.next_blocks.take_next()
        self.score_board = ScoreBoard(self.screen, x=300, y=740)
        self.pause_menu = PauseMenu(self.screen)
        self.game_over_menu = GameOverMenu(self.screen)

        # durumlar
        self.gravity_counter = 0
        self.soft_drop = False
        self.left_pressed = False
        self.left_pressed_tick = 0
        self.right_pressed = False
        self.right_pressed_tick = 0
        self.last_movement = pygame.time.get_ticks()
        self.last_spawn = pygame.time.get_ticks()
        self.last_pause = pygame.time.get_ticks()

        self.paused = False
        self.game_over = False

    def update(self, events: List[Event]):
        if self.paused:
            self.handle_pause_events(events)
        elif self.game_over:
            self.handle_gameover_events(events)
        else:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.esc()  # pause
                    elif event.key == Controls.hold:
                        self.hold()
                    elif event.key == Controls.rotate_cw:
                        self.rotate_cw()
                    elif event.key == Controls.rotate_ccw:
                        self.rotate_ccw()
                    elif event.key == Controls.hard_drop:
                        self.active_block.hard_drop()
                    elif event.key == Controls.soft_drop:
                        self.soft_drop = True
                    elif event.key == Controls.move_left:
                        self.left_pressed_tick = 0
                        self.left_pressed = True
                    elif event.key == Controls.move_right:
                        self.right_pressed_tick = 0
                        self.right_pressed = True
                if event.type == pygame.KEYUP:
                    if event.key == Controls.soft_drop:
                        self.soft_drop = False
                    elif event.key == Controls.move_left:
                        self.left_pressed = False
                    elif event.key == Controls.move_right:
                        self.right_pressed = False

            # Lock delays
            if pygame.time.get_ticks() - self.last_spawn > 20000:
                self.active_block.hard_drop()

            if pygame.time.get_ticks() - self.last_movement > max(500, 17.1/self.get_gravity()):  #  16.66/gravity = satır başına ms
                self.active_block.hard_drop()

            # Locking
            if self.active_block.locked:
                locked_out = self.board.add_block(self.active_block)
                lines_cleared = self.board.clear_lines()
                self.active_block = self.next_blocks.take_next()
                blocked_out = self.active_block.is_blocked_out()
                self.last_movement = pygame.time.get_ticks()
                self.last_spawn = pygame.time.get_ticks()
                self.score_board.add_cleared_lines(lines_cleared)
                if locked_out or blocked_out:
                    self.game_over = True
                    pygame.mixer.music.pause()
                    return

            # gravity
            if self.gravity_counter >= 1:
                gravity_floor = math.floor(self.gravity_counter)
                self.gravity_counter -= gravity_floor
                for i in range(gravity_floor):
                    if self.active_block.move_down():
                        self.last_movement = pygame.time.get_ticks()

            if self.soft_drop:
                self.gravity_counter += self.get_gravity()*20
            else:
                self.gravity_counter += self.get_gravity()

            # right/left movement
            if self.left_pressed:
                if (self.left_pressed_tick > 6 or self.left_pressed_tick == 0) and self.left_pressed_tick % 2 == 0:
                    if self.active_block.move_left():
                        self.last_movement = pygame.time.get_ticks()
                self.left_pressed_tick += 1
            if self.right_pressed:
                if (self.right_pressed_tick > 6 or self.right_pressed_tick == 0) and self.right_pressed_tick % 2 == 0:
                    if self.active_block.move_right():
                        self.last_movement = pygame.time.get_ticks()
                self.right_pressed_tick += 1

    def draw(self):
        self.board.draw()
        self.active_block.draw_ghost_piece()
        self.active_block.draw_on_board()
        self.hold_box.draw()
        self.next_blocks.draw()
        self.score_board.draw()
        if self.paused:
            self.pause_menu.draw()
        elif self.game_over:
            self.game_over_menu.draw()

    def get_gravity(self):
        return self.gravity_levels[self.score_board.level]

    def esc(self):
        self.last_pause = pygame.time.get_ticks()
        pygame.mixer.music.pause()
        self.paused = True

    def hold(self):
        if self.hold_box.can_swap(self.active_block):
            self.active_block.reset()
            self.active_block = self.hold_box.swap(self.active_block)
            if self.active_block is None:
                self.active_block = self.next_blocks.take_next()
                self.last_spawn = pygame.time.get_ticks()

    def rotate_cw(self):
        rotated = self.active_block.rotate_cw()
        if rotated:
            self.last_movement = pygame.time.get_ticks()

    def rotate_ccw(self):
        rotated = self.active_block.rotate_ccw()
        if rotated:
            self.last_movement = pygame.time.get_ticks()

    def handle_pause_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = False
                    pygame.mixer.music.unpause()
                    self.last_spawn += pygame.time.get_ticks() - self.last_pause
                    self.last_movement += pygame.time.get_ticks() - self.last_pause
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.pause_menu.resume_button.collidepoint(event.pos):
                    self.paused = False
                    pygame.mixer.music.unpause()
                    self.last_spawn += pygame.time.get_ticks() - self.last_pause
                    self.last_movement += pygame.time.get_ticks() - self.last_pause
                elif self.pause_menu.menu_button.collidepoint(event.pos):
                    self.app.start_menu()

    def handle_gameover_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if self.game_over_menu.menu_button.collidepoint(event.pos):
                    self.app.start_menu()

    def get_observation(self):
        """
        Creates and returns observation board for model
        :return: observation dictionary which contains board, active tetromino mask, holder, and queue
        """
        # creates observation dictionary
        # board includes pieces placed and active piece
        # active tetromino mask overlays square over active piece
        # holder has current piece being held
        # queue has next four pieces
        observation = {
            'board': np.ones((1, 24, 18), dtype=np.uint8),
            'active_tetromino_mask': np.ndarray((1, 24, 18), dtype=np.uint8),
            'holder': np.ones((1, 4, 4), dtype=np.uint8),
            'queue': np.ndarray((1, 4, 16), dtype=np.uint8)
        }

        # copy pygame board to observation board
        for r in range(self.board.horizontal_lines):
            for c in range(self.board.vertical_lines):
                observation['board'][0][r][c+4] = self.board.grid[r][c]

        # set active block to variable to just make it easier
        active_block = self.active_block

        # define block row location and column location
        block_r = active_block.grid_y
        block_c = active_block.grid_x

        # for every row in the active 4x4 piece grid
        for r in range(4):
            # for every column in the active 4x4 piece grid
            for c in range(4):
                # if the square is part of the piece
                if active_block.get_block_grid()[r][c] > 0:
                    # copy active piece square to observation board
                    observation['board'][0][block_r + r][block_c + c + 4] = active_block.get_block_grid()[r][c]

        # if there is a piece held
        if self.hold_box.block is not None:
            # copy held piece to observation holder
            observation['holder'][0] = np.asarray(self.hold_box.block.get_block_grid())

        # for every piece in the queue
        for b in range(4):
            # get piece
            block = self.next_blocks.next_blocks[b]
            # for every row in the 4x4 piece grid
            for r in range(4):
                # for every column in the 4x4 piece grid
                for c in range(4):
                    # copy queue piece to observation queue
                    observation['queue'][0][r][c+b*4] = block.get_block_grid()[r][c]

        # for every row in the active 4x4 piece grid
        for r in range(4):
            # for every column in the active 4x4 piece grid
            for c in range(4):
                # if the square is part of the piece's active layer
                if active_block.get_active_layer()[r][c] > 0:
                    # copy active layer square to observation active tetromino mask
                    observation['active_tetromino_mask'][0][block_r+r][block_c+c+4] = 1

        return observation