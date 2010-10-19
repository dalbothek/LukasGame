#! /usr/bin/python

import Tkinter
import sys
import time

BLOCKSIZE = 30
PLAYERSIZE = 25

SPEED = 5
GRAVITY = 0.5
HEIGHT = 8
TOLERANCE = 5

class Board:
    def __init__(self):
        self.setup()
        self.load()

    def mainloop(self):
        while not self.finished:
            self.player.step()
            time.sleep(0.01)
        print
        print "Congratulations! You won!"
        self.load(self.level + 1)

    def setup(self):
        print
        print "+---------------+"
        print "| LukasGame 0.1 |"
        print "+---------------+"
        print
        print "Move with arrow keys"
        print
        print "Loading board..."
        self.tk = Tkinter.Tk()
        self.canvas = Tkinter.Canvas(self.tk)
        self.canvas.pack()
        self.player = Player(self)
        self.tk.bind("<Left>", self.player.leftKey)
        self.tk.bind("<Right>", self.player.rightKey)
        self.tk.bind("<Up>", self.player.upKey)
        self.tk.bind("<KeyRelease>", self.player.release)
        self.level = 1


    def load(self, level=None):
        self.finished = False

        print

        if level:
            self.level = level
            path = str(level) + ".lvl"
            print "Loading level " + str(level) + "..."
        elif len(sys.argv) == 2:
            print "Loading custom level..."
            path = sys.argv[1]
        else:
            print "Loading level 1..."
            path = "1.lvl"
        
        try:
            f = open(path, "r")
            board = f.readlines()
            f.close()
        except:
            print
            print "Loading failed!"
            print "Loading builtin level..."
            board = ["111111111111111111111 ",
                     "133101010001100000001",
                     "133000000000100000001",
                     "133010101000000000001",
                     "111111111001100000001",
                     "100000000000000000001",
                     "100000000000000111111",
                     "100000111111111100001",
                     "100000000000000000001",
                     "100100000000000001001",
                     "100101100000000001011",
                     "100100000000000001001",
                     "100111111000011111101",
                     "100000001000000000001",
                     "120000100000000000011",
                     "111111111111111111111"]
        
        self.h = len(board)
        self.w = len(board[0]) - 1
        self.blocks = []
        self.goal = []
        self.start = []
        for y in range(self.h):
            for x in range(self.w):
                if board[y][x] == "1":
                    self.blocks.append(Block(x,y))
                elif board[y][x] == "2":
                    self.start = [x,y]
                elif board[y][x] == "3":
                    self.goal.append(Goal(x,y))

        self.draw()
        self.play()

    def draw(self):
        self.clear()
        self.canvas.config(height=self.h*BLOCKSIZE)
        self.canvas.config(width=self.w*BLOCKSIZE)
        for goal in self.goal:
            goal.draw(self.canvas)
        for block in self.blocks:
            block.draw(self.canvas)

    def clear(self):
        items = self.canvas.find_all()
        for item in items:
            self.canvas.delete(item)

    def play(self):
        assert len(self.start) == 2
        self.player.startAt(self.start[0], self.start[1])
        self.player.draw()
        self.mainloop()

    def allowstep(self, x, y):
        for block in self.blocks:
            if block.inside(x,y):
                return False
        return True

    def imhere(self, x, y):
        for goal in self.goal:
            if goal.inside(x,y):
                self.win()

    def win(self):
        self.finished = True
        
class Block:
    def __init__(self, x, y):
        self.x1 = self.coord(x)
        self.y1 = self.coord(y)
        self.x2 = self.coord2(x)
        self.y2 = self.coord2(y)

    def inside(self, x, y):
        return x > self.x1 and x < self.x2 and y > self.y1 and y < self.y2

    def coord(self, coord):
        return coord * BLOCKSIZE

    def coord2(self, coord):
        return (coord + 1) * BLOCKSIZE

    def draw(self, canvas):
        canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, {"fill": "black"})

class Player:
    def __init__(self, board):
        self.board = board
        self.left = 0
        self.right = 0

    def startAt(self, x, y):
        self.x = x * BLOCKSIZE + (BLOCKSIZE - PLAYERSIZE)/2
        self.y = y * BLOCKSIZE + (BLOCKSIZE - PLAYERSIZE)/2
        self.startx = self.x
        self.starty = self.y
        self.vx = 0
        self.vy = 0
        self.onground = False
        self.vr = 0
        self.vl = 0
        self.flying = 0

    def draw(self):
        x2 = self.x + PLAYERSIZE
        y2 = self.y + PLAYERSIZE
        
        self.me = self.board.canvas.create_rectangle(self.x, self.y, x2, y2, {"fill": "red"})

    def leftKey(self, e):
        self.left = e.keycode
        self.vl = 1
        self.updatevx()

    def rightKey(self, e):
        self.right = e.keycode
        self.vr = 1
        self.updatevx()

    def upKey(self, e):
        self.jump()

    def release(self, e):
        if e.keycode == self.left:
            self.vl = 0
        elif e.keycode == self.right:
            self.vr = 0
        self.updatevx()

    def updatevx(self):
        self.vx = self.vr - self.vl

    def jump(self):
        if self.onground or self.flying < TOLERANCE:
            self.vy = - HEIGHT
            self.onground = False
            self.flying = TOLERANCE

    def step(self):
        x = self.x
        y = self.y

        if self.vx != 0:
            for i in range(SPEED):
                x += self.vx
                if not self.allowstep(x, y):
                    x -= self.vx
                    break

        if self.vy != 0:
            vd = self.vy/abs(self.vy)
            for i in range(int(abs(self.vy))):
                y += vd
                if not self.allowstep(x, y):
                    y -= vd
                    self.onground = True
                    self.flying = 0
                    self.vy = 0
                    break
        elif self.allowstep(x, y+1):
            self.onground = False          

        if not self.onground:
            self.vy += GRAVITY
            self.flying += 1
        
        if y > 30*BLOCKSIZE:
            x = self.startx
            y = self.starty
            self.onground = False
            self.vy = 0        
        
        self.move(x, y)
        self.x = x
        self.y = y

    def move(self, x, y):
        self.board.canvas.move(self.me, x-self.x, y-self.y)
        self.board.canvas.update()
        self.board.imhere(x+PLAYERSIZE/2,y+PLAYERSIZE/2)

    def allowstep(self, x, y):
        if not self.board.allowstep(x, y):
            return False
        if not self.board.allowstep(x+PLAYERSIZE, y):
            return False
        if not self.board.allowstep(x, y+PLAYERSIZE):
            return False
        return self.board.allowstep(x+PLAYERSIZE, y+PLAYERSIZE)

class Goal(Block):
    def draw(self, canvas):
        canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, {"fill": "blue", "outline":"blue"})
        
Board()
