#!/usr/bin/env python3
#-*- coding: utf-8 -*-
# Copyright (c) 2010 "Laria Carolin Chabowski"<me@laria.me>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from random import randrange as rand
from enum import Enum
import pygame, sys
import numpy as np
import math
from copy import deepcopy

# The configuration
cell_size =	18
cols =		10
rows =		22
maxfps = 	30

colors = [
(0,   0,   0  ),
(255, 85,  85),
(100, 200, 115),
(120, 108, 245),
(255, 140, 50 ),
(50,  120, 52 ),
(146, 202, 73 ),
(150, 161, 218 ),
(35,  35,  35) # Helper color for background grid
]

# Define the shapes of the single parts
tetris_shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]

def rotate_clockwise(shape):
    return [[shape[y][x] for y in range(len(shape)) ] for x in range(len(shape[0]) - 1, -1, -1)]

def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[cy + off_y ][cx + off_x ]:
                    return True
            except IndexError:
                return True
    return False

def remove_row(board, row):
    board[row].clear()
    return [[0 for i in range(cols)]] + board

def join_matrices(mat1, mat2, mat2_off):
	off_x, off_y = mat2_off
	for cy, row in enumerate(mat2):
		for cx, val in enumerate(row):
			mat1[cy+off_y-1	][cx+off_x] += val
	return mat1

def new_board():
	board = [[0 for x in range(cols)] for y in range(rows)]
	board += [[1 for x in range(cols)]]
	return board

class Moves(Enum):
    LEFT  = 1
    RIGHT = 2
    DROP  = 3
    ROT   = 4

class TetrisApp(object):
    def __init__(self, training=False):
        pygame.init()
        pygame.key.set_repeat(250,25)
        self.width = cell_size*(cols + 6)
        self.height = cell_size*rows
        self.rlim = cell_size*cols
        self.bground_grid = [[ 8 if x % 2 == y % 2 else 0 for x in range(cols)] for y in range(rows)]

        self.default_font = pygame.font.Font(pygame.font.get_default_font(), 12)

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        # We do not need mouse movement events, so we block them.
        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.training = training
        self.init_game()

    def new_stone(self):
        self.stone = self.next_stone[:]
        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.stone_x = int(cols / 2 - len(self.stone[0])/2)
        self.stone_y = 0

        if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
            self.gameover = True

    def init_game(self):
        self.board = new_board()
        self.new_stone()
        self.level = 1
        self.score = 0
        self.lines = 0
        pygame.time.set_timer(pygame.USEREVENT+1, 1000)

    def disp_msg(self, msg, topleft):
        x,y = topleft
        for line in msg.splitlines():
            self.screen.blit(self.default_font.render(line, False, (255,255,255), (0,0,0)), (x,y))
            y+=14

    def center_msg(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image =  self.default_font.render(line, False, (255,255,255), (0,0,0))

            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2

            self.screen.blit(msg_image, (self.width // 2-msgim_center_x, self.height // 2-msgim_center_y+i*22))

    def draw_matrix(self, matrix, offset):
        off_x, off_y  = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(self.screen, colors[val],
                                     pygame.Rect((off_x+x) * cell_size, (off_y+y) * cell_size, cell_size, cell_size), 0)

    def add_cl_lines(self, n):
        linescores = [0, 40, 100, 300, 1200]
        self.lines += n
        self.score += linescores[n] * self.level
        if self.lines >= self.level*6:
            self.level += 1
            newdelay = 1000-50*(self.level-1)
            newdelay = 100 if newdelay < 100 else newdelay
            pygame.time.set_timer(pygame.USEREVENT+1, newdelay)

    def move(self, delta_x):
        if not self.gameover and not self.paused:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.stone[0]):
                new_x = cols - len(self.stone[0])
            if not check_collision(self.board, self.stone, (new_x, self.stone_y)):
                self.stone_x = new_x

    def quit(self):
        self.center_msg("Exiting...")
        pygame.display.update()
        sys.exit()

    def drop(self, manual):
        if not self.gameover and not self.paused:
            self.score += 1 if manual else 0
            self.stone_y += 1
            if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
                print("AT BOTTOM")
                self.board = join_matrices(self.board, self.stone, (self.stone_x, self.stone_y))
                self.new_stone()
                cleared_rows = 0
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = remove_row(self.board, i)
                            cleared_rows += 1
                            break
                        else:
                            break
                self.add_cl_lines(cleared_rows)
                return True
        return False

    def insta_drop(self):
        if not self.gameover and not self.paused:
            while(not self.drop(True)):
                pass
            print("DONE INSTADROPPING")

    def rotate_stone(self):
        if not self.gameover and not self.paused:
            print("ROTATING STONE")
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board, new_stone, (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def toggle_pause(self):
        self.paused = not self.paused

    def start_game(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    def run(self):
        key_actions = {
            'ESCAPE':	self.quit,
            'LEFT':		lambda:self.move(-1),
            'RIGHT':	lambda:self.move(+1),
            'DOWN':		lambda:self.drop(True),
            'UP':		self.rotate_stone,
            'p':		self.toggle_pause,
            'SPACE':	self.start_game,
            'RETURN':	self.insta_drop
		}

        self.gameover = False
        self.paused = False

        dont_burn_my_cpu = pygame.time.Clock()
        while True:
            self.screen.fill((0,0,0))
            if self.gameover:
                self.center_msg("""Game Over!\nYour score: %d\nPress space to continue""" % self.score)
            else:
                if self.paused:
                    self.center_msg("Paused")
                else:
                    pygame.draw.line(self.screen, (255,255,255),
                                     (self.rlim+1, 0), (self.rlim+1, self.height-1))
                    self.disp_msg("Next:", (self.rlim+cell_size, 2))
                    self.disp_msg("Score: %d\n\nLevel: %d\nLines: %d" % (self.score, self.level, self.lines),
                                  (self.rlim+cell_size, cell_size*5))
                    self.draw_matrix(self.bground_grid, (0,0))
                    self.draw_matrix(self.board, (0,0))
                    self.draw_matrix(self.stone, (self.stone_x, self.stone_y))
                    self.draw_matrix(self.next_stone, (cols+1,2))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT+1:
                    self.drop(False)
                elif event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_" + key):
                            key_actions[key]()

            dont_burn_my_cpu.tick(maxfps)

    def run_brain(self, weights):
        brain_actions = {
            Moves.LEFT:  lambda:self.move(-1),
            Moves.RIGHT: lambda:self.move(1),
            Moves.DROP:  self.insta_drop,
            Moves.ROT:   self.rotate_stone
        }

        self.init_game()
        self.gameover = False
        self.paused = False
        brain = Brain(weights)
        dont_burn_my_cpu = pygame.time.Clock()
        while True:
            if self.training:
                # training
                if self.gameover:
                    return self.score
                else:
                    brain.set_board(self.board, self.stone)
                    next_moves = brain.get_best_move()
                    print(next_moves)
                    for move in next_moves:
                        brain_actions[move]()
                dont_burn_my_cpu.tick(1000)
            else:
                # TODO run the brain with graphics
                pass

class Data:
    def __init__(self, board, stone, stone_x, stone_y):
        self.board = board
        self.stone = stone
        self.stone_x = stone_x
        self.stone_y = stone_y

    @staticmethod
    def clone(data):
        return Data(deepcopy(data.board), data.stone[:], data.stone_x, data.stone_y)


# determines the best moves according to the weights it is given
class Brain:
    def __init__(self, weights):
        self.weights = weights

    def set_board(self, board, stone):
        self.num_rows = len(board) - 1
        self.num_cols = len(board[0])
        self.begin_state = Data(board, stone, int(self.num_cols / 2 - len(stone[0])/2), 0)

    # enumerate all the possible move combinations, then score them
    def get_best_move(self):
        (moves, states) = self.enumerate(self.begin_state)
        scores = list()
        for state in states:
            score = self.weights[0] * self.aggregate_height(state) + self.weights[1] * self.complete_lines(state) + self.weights[2] * self.num_holes(state) + self.weights[3] * self.bumpiness(state)
            scores.append(score)
        return moves[scores.index(max(scores))]

    # returns ([list of move combinations], [list of Data states])
    def enumerate(self, begin_state):
        moves = list()
        states = list()

        # go through with original orientation
        temp = Data.clone(begin_state)
        moves.append([Moves.DROP])
        self.insta_drop(temp)
        states.append(temp)

        # now translate the normal orientation
        temp = Data.clone(begin_state)
        num_left = 0
        while self.move(temp, -1):
            # left translations
            num_left += 1
            moves.append([Moves.LEFT] * num_left + [Moves.DROP])
            drop_temp = Data.clone(temp)
            self.insta_drop(drop_temp)
            states.append(drop_temp)
        temp = Data.clone(begin_state)
        num_right = 0
        while self.move(temp,1):
            # right translations
            num_right += 1
            moves.append([Moves.RIGHT] * num_right + [Moves.DROP])
            drop_temp = Data.clone(temp)
            self.insta_drop(drop_temp)
            states.append(drop_temp)

        # now go through the rotations
        temp = Data.clone(begin_state)
        num_rot = 0
        while self.rotate_stone(temp):
            num_rot += 1

            rot_temp = Data.clone(temp)
            moves.append([Moves.ROT] * num_rot + [Moves.DROP])
            self.insta_drop(rot_temp)
            states.append(rot_temp)

            # now translate the rotated orientation
            rot_temp = Data.clone(temp)
            num_left = 0
            while self.move(rot_temp, -1):
                # left translations
                num_left += 1
                moves.append([Moves.ROT] * num_rot + [Moves.LEFT] * num_left + [Moves.DROP])
                drop_temp = Data.clone(rot_temp)
                self.insta_drop(drop_temp)
                states.append(drop_temp)
            rot_temp = Data.clone(temp)
            num_right = 0
            while self.move(temp, 1):
                # right translations
                num_right += 1
                moves.append([Moves.ROT] * num_rot + [Moves.RIGHT] * num_right + [Moves.DROP])
                drop_temp = Data.clone(rot_temp)
                self.insta_drop(drop_temp)
                states.append(drop_temp)

        return (moves, states)

    # returns True if translation was successful
    def move(self, data, delta_x):
        new_x = data.stone_x + delta_x
        if new_x < 0:
            return False
        if new_x > self.num_cols - len(data.stone[0]):
            return False
        if not check_collision(data.board, data.stone, (new_x, data.stone_y)):
            data.stone_x = new_x
            return True
        return False

    # returns True if rotate was successful
    def rotate_stone(self, data):
        new_stone = rotate_clockwise(data.stone)
        if not check_collision(data.board, new_stone, (data.stone_x, data.stone_y)):
            data.stone = new_stone
            return True
        return False

    def insta_drop(self, data):
        while not self.drop(data):
            pass

    def drop(self, data):
        data.stone_y += 1
        if check_collision(data.board, data.stone, (data.stone_x, data.stone_y)):
            data.board = join_matrices(data.board, data.stone, (data.stone_x, data.stone_y))
            return True
        return False

    # get the height of each column in the board
    # returns a list with length = num_cols
    # each entry represents the height of that column in the board
    def heights(self, data):
        heights = list()
        for col in range(self.num_cols):
            count = 0
            # go through each column starting from the top, stop when a block is found
            for row in range(self.num_rows):
                if data.board[row][col] == 0:
                    count += 1
                else:
                    break

            heights.append(self.num_rows - count)
        return heights

    # calculate the sum of the heights of all columns in the board
    def aggregate_height(self, data):
        return sum(self.heights(data))

    # calculate the number of filled rows
    def complete_lines(self, data):
        count = 0
        for line in data.board:
            if 0 not in line:
                count += 1
        return count

    # calculate the number of holes
    # a hole is defined as an empty space with a filled space above it
    def num_holes(self, data):
        num_holes = 0
        for col in range(self.num_cols):
            num_empty = 0
            for row in range(self.num_rows - 1, -1, -1):
                if data.board[row][col] == 0:
                    num_empty += 1
                else:
                    num_holes += num_empty
                    num_empty = 0
        return num_holes

    # calculate the bumpiness of the board
    def bumpiness(self, data):
        board_heights = self.heights(data)
        bumpiness = 0
        for i in range(self.num_cols - 1):
            bumpiness += abs(board_heights[i] - board_heights[i + 1])
        return bumpiness

if __name__ == '__main__':
    App = TetrisApp()
    App.run()
