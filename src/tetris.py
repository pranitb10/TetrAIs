from random import randrange as rand
import pygame, sys

# Initial Game config/state
cellSize = 18
cols = 10
rows = 22
maxFps = 30

colors = [
    (0, 0, 0),
    (255, 85, 85),
    (100, 200, 115),
    (120, 108, 245),
    (255, 140, 50),
    (50, 120, 52),
    (146, 202, 73),
    (150, 161, 218),
    # Color for the background cell-grid:
    (35, 35, 35)
]

tetrisShapes = [
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


def rotateClockwise(shape):
    return [[shape[y][x]
             for y in range(len(shape))]
            for x in range(len(shape[0]) - 1, -1, -1)]


def checkCollision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[cy + off_y][cx + off_x]:
                    return True
            except IndexError:
                return True
    return False


def removeRow(board, row):
    del board[row]
    return [[0 for i in range(cols)]] + board


def joinMatrices(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy + off_y - 1][cx + off_x] += val
    return mat1


def newBoard():
    board = [[0 for x in range(cols)]
             for y in range(rows)]
    board += [[1 for x in range(cols)]]
    return board


class TetrisApp(object):
    def __init__(self):
        self.paused = None
        self.lines = None
        self.score = None
        self.level = None
        self.board = None
        self.gameOver = None
        self.stone_y = None
        self.stone_x = None
        self.stone = None
        pygame.init()
        pygame.key.set_repeat(250, 25)
        self.width = cellSize * (cols + 6)
        self.height = cellSize * rows
        self.rlim = cellSize * cols
        self.bground_grid = [[8 if x % 2 == y % 2 else 0 for x in range(cols)] for y in range(rows)]

        self.default_font = pygame.font.Font(
            pygame.font.get_default_font(), 12)

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.event.set_blocked(pygame.MOUSEMOTION)

        self.next_stone = tetrisShapes[rand(len(tetrisShapes))]
        self.init_game()

    def new_stone(self):
        self.stone = self.next_stone[:]
        self.next_stone = tetrisShapes[rand(len(tetrisShapes))]
        self.stone_x = int(cols / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0

        if checkCollision(self.board,
                          self.stone,
                          (self.stone_x, self.stone_y)):
            self.gameOver = True
        self.score += 1

    def init_game(self):
        pygame.time.set_timer(pygame.USEREVENT + 1, 750)
        self.board = newBoard()
        self.level = 1
        self.score = 0
        self.lines = 0
        self.gameOver = False
        self.paused = False
        self.new_stone()

    def displayMessage(self, msg, topLeft):
        x, y = topLeft
        for line in msg.splitlines():
            self.screen.blit(
                self.default_font.render(
                    line,
                    False,
                    (255, 255, 255),
                    (0, 0, 0)),
                (x, y))
            y += 14

    def centerMessage(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image = self.default_font.render(line, False,
                                                 (255, 255, 255), (0, 0, 0))

            msg_image_center_x, msg_image_center_y = msg_image.get_size()
            msg_image_center_x //= 2
            msg_image_center_y //= 2

            self.screen.blit(msg_image, (
                self.width // 2 - msg_image_center_x,
                self.height // 2 - msg_image_center_y + i * 22))

    def drawMatrix(self, matrix, offset):
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        self.screen,
                        colors[val],
                        pygame.Rect(
                            (off_x + x) *
                            cellSize,
                            (off_y + y) *
                            cellSize,
                            cellSize,
                            cellSize), 0)

    def addClLines(self, n):
        lineScores = [0, 40, 100, 300, 1200]
        self.lines += n
        self.score += lineScores[n]

    def move(self, delta_x):
        if not self.gameOver and not self.paused:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.stone[0]):
                new_x = cols - len(self.stone[0])
            if not checkCollision(self.board,
                                  self.stone,
                                  (new_x, self.stone_y)):
                self.stone_x = new_x

    def quit(self):
        self.centerMessage("Exiting...")
        pygame.display.update()
        sys.exit()

    def drop(self, manual):
        if not self.gameOver and not self.paused:
            # self.score += 1 if manual else 0
            self.stone_y += 1
            if checkCollision(self.board,
                              self.stone,
                              (self.stone_x, self.stone_y)):
                self.board = joinMatrices(
                    self.board,
                    self.stone,
                    (self.stone_x, self.stone_y))
                cleared_rows = 0
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = removeRow(
                                self.board, i)
                            cleared_rows += 1
                            break
                    else:
                        break
                self.addClLines(cleared_rows)
                self.new_stone()
                return True
        return False

    def instantDrop(self):
        if not self.gameOver and not self.paused:
            while not self.drop(True):
                pass

    def rotateStone(self):
        if not self.gameOver and not self.paused:
            new_stone = rotateClockwise(self.stone)
            if not checkCollision(self.board,
                                  new_stone,
                                  (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def togglePause(self):
        self.paused = not self.paused

    def startGame(self):
        if self.gameOver:
            self.init_game()
            self.gameOver = False

    def run(self):
        key_actions = {
            'ESCAPE': self.quit,
            'LEFT': lambda: self.move(-1),
            'RIGHT': lambda: self.move(+1),
            'DOWN': lambda: self.drop(True),
            'UP': self.rotateStone,
            'p': self.togglePause,
            'SPACE': self.startGame,
            'RETURN': self.instantDrop
        }

        self.gameOver = False
        self.paused = False

        prevent_cpu_burnout = pygame.time.Clock()
        while 1:
            self.screen.fill((0, 0, 0))
            if self.gameOver:
                self.centerMessage("Game Over!\nYour score: %d\nPress space to continue" % self.score)
            else:
                pygame.draw.line(self.screen,
                                 (255, 255, 255),
                                 (self.rlim + 1, 0),
                                 (self.rlim + 1, self.height - 1))
                self.displayMessage("Next:", (
                    self.rlim + cellSize,
                    2))
                self.displayMessage("Score: %d\n\nLevel: %d\nLines: %d" % (self.score, self.level, self.lines),
                                    (self.rlim + cellSize, cellSize * 5))
                self.drawMatrix(self.bground_grid, (0, 0))
                self.drawMatrix(self.board, (0, 0))
                self.drawMatrix(self.stone,
                                (self.stone_x, self.stone_y))
                self.drawMatrix(self.next_stone,
                                (cols + 1, 2))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.bestMoves()
                elif event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_"
                                             + key):
                            key_actions[key]()

            prevent_cpu_burnout.tick(maxFps)

    def bestMoves(self):
        self.instantDrop()


if __name__ == '__main__':
    App = TetrisApp()
    App.run()
