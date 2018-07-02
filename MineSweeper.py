import random
#Minesweeper Game
#Allows for the g.e. to do clicks and flags on a minesweeper board
class Mines:
    #0   nothing
    # -1 mine
    # n  number
    #-2  flag
    def __init__(self, size=10, minesN = 20):
        self.size = size
        self.board = []
        self.pBoard = []
        self.xDir = [-1, 0, 1]
        self.yDir = [-1, 0, 1]
        self.xFloodDir = [-1, 1, 0, 0]
        self.yFloodDir = [0, 0, -1, 1]

        for i in range(0, size):
            self.board.append([])
            self.pBoard.append([])
            for j in range(0, size):
                self.board[i].append(0)
                self.pBoard[i].append(-3)

        for i in range(0, minesN):
            finishedFlag = False
            while not finishedFlag:
                x = random.randint(0, self.size-1)
                y = random.randint(0, self.size-1)

                if self.board[x][y] == 0:
                    self.board[x][y] = -1
                    finishedFlag = True

        for i in range(0, self.size):
            for j in range(0, self.size):
                if self.board[i][j] == 0:
                    minesCount = 0
                    for k in range(0, len(self.xDir)):
                        for l in range(0, len(self.yDir)):
                            if self.validate(i + self.xDir[k], j + self.yDir[l]):
                                if self.board[i+self.xDir[k]][j+self.yDir[l]] == -1:
                                    minesCount += 1
                    self.board[i][j] = minesCount
        # for i in range(0, self.size):
        #     tString = ""
        #     for j in range(0, self.size):
        #         tString += str(self.board[i][j]) + "\t"
        #     tString += "\n"
        #     print(tString)
    def printBoard(self):
        for i in range(0, self.size):
            tString = ""
            for j in range(0, self.size):
                tString += str(self.board[i][j]) + "\t"
            tString += "\n"
            print(tString)
    def printPBoard(self):
        for i in range(0, self.size):
            tString = ""
            for j in range(0, self.size):
                tString += str(self.pBoard[i][j]) + "\t"
            tString += "\n"
            print(tString)

    #fills out all the 0's and adjacent fields
    def flood(self, x, y):
        self.pBoard[x][y] = 0
        for i in range(0, len(self.xFloodDir)):
            for j in range(0, len(self.yFloodDir)):
                    if self.validate(x + self.xFloodDir[i], y + self.yFloodDir[j]):
                        if self.pBoard[x + self.xFloodDir[i]][y + self.yFloodDir[j]] == -3:
                            if self.board[x + self.xFloodDir[i]][y + self.yFloodDir[j]] == 0:
                                self.flood(x + self.xFloodDir[i], y + self.yFloodDir[j])
                            else:
                                self.select(x + self.xFloodDir[i], y + self.yFloodDir[j], "click")

    #clicks a "zero" on the board to make it easier to find subsequent clicks
    def selectZeroFirst(self):
        for i in range(0, self.size):
            for j in range(0, self.size):
                if self.board[i][j] == 0:
                    self.select(i,j,"click")
                    return
        return

    #takes in a coordinate and an action ("click" or "flag).
    #returns True is the move is allowed and carries out the move, and False otherwise
    def select(self, x, y, action):
        if self.validate(x, y):
            if self.pBoard[x][y] == -3:
                if action == "click":
                    if self.board[x][y] > -1:
                        if self.board[x][y] == 0:
                            self.flood(x, y)
                            return True
                        else:
                            self.pBoard[x][y] = self.board[x][y]
                            return True
                elif action == "flag":
                    if self.board[x][y] == -1:
                        self.pBoard[x][y] = -2
                        return True
        return False

    #checks if coordinate is valid
    def validate(self, x, y):
        if x > -1 and x < self.size and y > -1 and y < self.size:
            return True
        return False
    # def drawSomething(self):
    #     g = GraphWin("hi", 500, 500)
    #     circ = Circle(Point(100, 450), 10)
    #     circ.setFill('blue')
    #     circ.draw(g)