from tetris import *


class TetrisGreedy(TetrisApp):

    def bestMoves(self):
        x, low = 0, 0
        for j in range(len(self.board[0])):
            i = 0
            while not self.board[i][j]:
                i += 1
            if i > low:
                x, low = j, i

        self.move(x - self.stone_x)
        self.instantDrop()


if __name__ == '__main__':
    App = TetrisGreedy()
    App.run()
