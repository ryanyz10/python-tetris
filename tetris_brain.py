# gets the height of each column in the board
# returns a list with each element corresponding to the height in the column
def heights(board):
    num_rows = len(board)
    num_cols = len(board[0])
    heights = list()
    for col in range(num_cols):
        count = 0
        for row in range(num_rows - 1, -1, -1):
            if board[row][col] == 0:
                break
            count += 1
        heights.append(count)

    return heights


def complete_lines(board):
    count = 0
    for line in board:
        if 0 not in line:
            count += 1

    return count

def num_holes(board):
    pass

def bumpiness(board):

    pass

class Brain:
    def __init__(self, board):
        self.board = board

    def test_move(self):
        pass

# aggregate height can be calculated from sum(heights(board))
# heights(board) will be stored somewhere
