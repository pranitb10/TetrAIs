from tetris import TetrisApp
from state import *


class depthLimitedGreedy(object):

    def __init__(self, state):
        self.board = state.board
        self.lineScore = state.score
        self.heights = self.getHeights()
        self.score = self.evaluate()

    def evaluate(self):
        f0 = self.getLinesCleaned()
        f1 = self.getTotalHeight()
        f2 = self.getMaxHeight()
        f3 = self.getHoles()
        f4 = self.getDeltas()

        score = 4 * f0 - 2 * f1 - f3 - f4
        return score

    def getHeights(self):
        heights = []
        for x in range(COLS):
            heights.append(0)
            for y in range(ROWS):
                if self.board[y][x]:
                    heights[x] = ROWS - y
                    break
        return heights

    def getTotalHeight(self):
        return sum(self.heights)

    def getMaxHeight(self):
        return max(self.heights)

    def getLinesCleaned(self):
        return ([0, 40, 100, 300, 1200]).index(self.lineScore)

    def getDeltas(self):
        res = 0
        for i, h in enumerate(self.heights):
            if i:
                res += abs(self.heights[i] - self.heights[i - 1])
        return res

    def getHoles(self):
        res = 0
        for x in range(COLS):
            flag = False
            for y in range(ROWS):
                if self.board[y][x]:
                    flag = True
                elif flag:
                    res += 1
        return res


def oneBestMove(state):
    bestScore, bestAction = float("-inf"), None
    for rotateN in range(4):
        for x in range(COLS):
            action = (rotateN, x)
            nextStates = state.nextStates(action)
            if len(nextStates):
                score = depthLimitedGreedy(nextStates[0]).score
                if score > bestScore:
                    bestScore, bestAction = score, action
    return bestScore


class TetrisGreedy(TetrisApp):

    def bestMoves(self):
        bestScore, bestAction = float("-inf"), None
        initState = State(self.board, self.score, self.stone, self.next_stone)
        for rotateN in range(4):
            for x in range(COLS):
                action = (rotateN, x)
                nextStates = initState.nextStates(action)
                if len(nextStates):
                    score = oneBestMove(nextStates[0])
                    if score > bestScore:
                        bestScore, bestAction = score, action

        if not self.gameOver:
            for _ in range(bestAction[0]):
                self.rotateStone()
            self.move(bestAction[1] - self.stone_x)
            self.instantDrop()


if __name__ == '__main__':
    App = TetrisGreedy()
    App.run()
