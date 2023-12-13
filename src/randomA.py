from tetris import *
from random import randrange as rand


class TetrisRandom(TetrisApp):
    def bestMoves(self):
        for _ in range(rand(4)):
            self.rotateStone()

        if rand(2):
            for _ in range(rand(6)):
                self.move(-1)
        else:
            for _ in range(rand(6)):
                self.move(+1)

        self.instantDrop()


if __name__ == '__main__':
    App = TetrisRandom()
    App.run()
