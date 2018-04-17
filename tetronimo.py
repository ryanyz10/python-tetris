import pygame
import sys
import time
import random

from pygame.locals import *

import numpy

# game constants
FPS = 25

# TODO change the window size
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
BOX_SIZE = 20

# TODO tinker with this
# the extra rows/columns are for a border of boxes
BOARD_WIDTH = 12
BOARD_HEIGHT = 22
BLANK = '.'
MOVE_SIDEWAYS_FREQ = 0.15
MOVE_DOWN_FREQ = 0.1

# window margins
X_MARGIN = int((WINDOW_WIDTH - BOX_SIZE * BOARD_WIDTH) / 2)
Y_MARGIN = int((WINDOW_HEIGHT - BOX_SIZE * BOARD_HEIGHT) / 2)

# colors
WHITE = (255, 255, 255)
GRAY = (185, 185, 185)
BLACK = (0, 0, 0)

RED = (155, 0, 0)
L_RED = (175, 20, 20)

GREEN = (0, 155, 0)
L_GREEN = (20, 175, 20)

BLUE = (0, 0, 155)
L_BLUE = (20, 20, 175)

YELLOW = (155, 155, 0)
L_YELLOW = (175, 175, 20)

# TODO change the colors around
# look into a gradient effect
BORDER_COLOR = BLUE
BG_COLOR = BLACK
TEXT_COLOR = WHITE
TEXT_SHADOW_COLOR = GRAY
COLORS = (RED, GREEN, BLUE, YELLOW)
L_COLORS = (L_RED, L_GREEN, L_BLUE, L_YELLOW)

assert len(COLORS) == len(L_COLORS)

SHAPES = ('S', 'Z', 'I', 'O', 'L', 'J', 'T')


class Shape:
    def __init__(self, shape):
        self.shape = shape;
        if shape is 'S':
            self.width = 3
            self.height = 3
            self.template = ['OO.',
                             '.OO',
                             '...']
        elif shape is 'Z':
            self.width = 3
            self.height = 3
            self.template = ['.OO',
                             'OO.'
                             '...']
        elif shape is 'I':
            self.width = 4
            self.height = 4
            self.template = ['....',
                             'OOOO',
                             '....',
                             '....']
        elif shape is 'O':
            self.width = 4
            self.height = 3
            self.template = ['.OO.',
                             '.OO.',
                             '....']
        elif shape is 'L':
            self.width = 3
            self.height = 3
            self.template = ['..O',
                             'OOO',
                             '...']
        elif shape is 'J':
            self.width = 3
            self.height = 3
            self.template = ['O..',
                             'OOO',
                             '...']
        elif shape is 'T':
            self.width = 3
            self.height = 3
            self.template = ['.O.',
                             'OOO',
                             '...']

    # TODO write the rotation code on my own
    def rotateCW(self):
        if self.shape is 'O':
            return

        self.template = numpy.rot90(self.template, k=3).tolist()

    def rotateCCW(self):
        if self.shape is 'O':
            return

        self.template = numpy.rot90(self.template).tolist()


def main():
    global FPS_CLOCK, DISPLAY_SURF, BASIC_FONT, BIG_FONT
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    BASIC_FONT = pygame.font.Font('freesansbold.ttf', 18)
    BIG_FONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetromino')

    showTextScreen('Tetromino')

    # game loop
    while True:
        # TODO music
        runGame()
        showTextScreen('Game Over')


# TODO what will i need to incorporate a neural net?
# some way to calculate fitness -> score
# some way for the neural net to make moves
# some way for the neural net to simulate moves
def runGame(training=False):
    board = getBlankBoard()
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    lastFallTime = time.time()
    movingDown = False
    movingLeft = False
    movingRight = False

    score = 0
    level, fallFreq = calculateLevelAndFallFreq(score)

    # these methods will probably have to change with my modification
    # I will also need to handle wall-kicks
    fallingPiece = getNewPiece()
    nextPiece = getNewPiece()


