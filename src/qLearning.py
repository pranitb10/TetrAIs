from tetris import TetrisApp
from state import *
import random as rand

EPSILON, ALPHA = 0.1, 0.1

qValues = {}
weights = [1, -1, -1, -1, -1]


class QL(object):

    def __init__(self, state):
        self.state = state
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

        score = weights[0] * f0 - weights[1] * f1 - weights[2] * f2 - weights[3] * f3 - weights[4] * f4
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
        s = [0, 40, 100, 300, 1200]
        if self.lineScore in s:
            return ([0, 40, 100, 300, 1200]).index(self.lineScore)
        else:
            return 0

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


class TetrisRL(TetrisApp):

    def bestMoves(self):
        bestScore, bestAction = float("-inf"), None
        initState = State(self.board, self.score, self.stone, self.next_stone)

        # update weights
        if rand.random() < EPSILON:
            rotateN = rand.randrange(4)
            if rotateN & 1:
                maxX = COLS - len(initState.block) + 1
            else:
                maxX = COLS - len(initState.block[0]) + 1
            x = rand.randrange(maxX)
            action = (rotateN, x)
            nextStates = initState.nextStates(action)
            if len(nextStates):
                nextState = nextStates[0]
                for i, w in enumerate(weights):
                    weights[i] += ALPHA * (nextState.score + QL(nextState).evaluate() - QL(initState).evaluate())
        else:
            for rotateN in range(4):
                for x in range(COLS):
                    action = (rotateN, x)
                    nextStates = initState.nextStates(action)
                    if len(nextStates):
                        score = QL(nextStates[0]).score
                        if score > bestScore:
                            bestScore, bestAction = score, action

            nextStates = initState.nextStates(bestAction)
            if len(nextStates):
                nextState = nextStates[0]
                for i, w in enumerate(weights):
                    weights[i] += ALPHA * (nextState.score + QL(nextState).evaluate() - QL(initState).evaluate())

        # pick best action based on updated value
        for rotateN in range(4):
            for x in range(COLS):
                action = (rotateN, x)
                nextStates = initState.nextStates(action)
                if len(nextStates):
                    score = QL(nextStates[0]).score
                    if score > bestScore:
                        bestScore, bestAction = score, action

        if not self.gameOver:
            for _ in range(bestAction[0]):
                self.rotateStone()
            self.move(bestAction[1] - self.stone_x)
            self.instantDrop()
            print(weights)


if __name__ == '__main__':
    App = TetrisRL()
    App.run()
