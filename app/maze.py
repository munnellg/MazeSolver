#!/usr/bin/env python3
import random
from queue import Queue, LifoQueue

class Cell:
    NORMAL    = 0
    ANALYZING = 1
    FOLLOWING = 2

    def __init__(self, path):
        self.paths  = path
        self.route  = (0,0)
        self.status = 0

    def add_path(self, path):
        self.paths.append(path)

    def get_paths(self):
        return self.paths

    def num_paths(self):
        return len(self.paths)

    def set_status(self, status):
        self.status = status

    def get_status(self):
        return self.status

    def get_route(self):
        return self.route

    def set_route(self, route):
        self.route = route

    def has_route(self):
        return self.route[0] != 0 or self.route[1] != 0

    def __str__(self):
        return "({:>2},{:>2}) ".format(self.route[0], self.route[1])

class CellScore:
    def __init__(self, gscore, fscore):
        self.gscore = gscore
        self.fscore = fscore
        self.path   = (0,0)

    def get_gscore(self):
        return self.gscore

    def set_gscore(self, gscore):
        self.gscore = gscore

    def get_fscore(self):
        return self.fscore

    def set_fscore(self, fscore):
        self.fscore = fscore

    def get_path(self):
        return self.path

    def set_path(self, x, y):
        self.path = (x,y)


class Maze:
    WALL = 1
    TILE = 0
    def __init__(self, width, height, start=(0,0), end=-1):
        self.width = width
        self.height = height

        # Start is top left, end is bottom right by default
        self.start = start
        if end < 0:
            self.end = (self.width-1, self.height-1)
        else:
            self.end = end

        # Empty maze. Could just as easily init to None, but I prefer
        # to have something there
        self.maze = [[Cell([]) for i in range(width)] for j in range(height) ]

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_tile(self, x, y):
        return self.maze[y][x]

    def step_generate(self):
        self.generator()

    def __str__(self):
        string = ""
        for line in self.maze:
            for element in line:
                string += "{}".format(element)
            string +="\n"
        return string[:-1]

class DepthFirstSearchGenerator:
    def __init__(self, maze):
        self.maze = maze

        paths = [(0,1), (0,-1), (1,0), (-1,0)]
        random.shuffle(paths)

        start_pos = self.maze.get_start()
        self.stack = [(start_pos[0], start_pos[1], paths)]
        node = self.maze.get_tile(start_pos[0], start_pos[1])
        node.set_status(Cell.ANALYZING)

    def generate(self):
        while True:
            if not self.step():
                return

    def step(self):
        # Stack is empty. We've nowhere left to go. Return False to
        # show that we're done
        if len(self.stack) == 0:
            return False

        node = self.stack[-1]
        paths = node[2]

        # Pick a path to follow
        path = paths.pop()

        # Get coordinates of this node and the targeted neighbour node
        x  = node[0]
        y  = node[1]
        x2 = x + path[0]
        y2 = y + path[1]

        node = self.maze.get_tile(x, y)

        # If this is the last valid direction for this node, remove
        # the node from the stack. It's no longer interesting
        if len(paths)==0:
            node.set_status(Cell.NORMAL)
            self.stack.pop()

        # Target node is invalid. Pick another by recursing
        if x2<0 or y2<0 or x2>=self.maze.get_width() or y2>=self.maze.get_height():
            return self.step()

        target = self.maze.get_tile(x2, y2)

        # Target node has already been visited. Pick another by
        # recursing
        if len(target.get_paths()) > 0:
            return True

        # Add new node to our path and push it to the stack so we can
        # continue generating along this new path
        target.add_path((-path[0], -path[1]))
        node.add_path(path)
        paths = [(0,1), (0,-1), (1,0), (-1,0)]
        random.shuffle(paths)
        self.stack.append((x2, y2, paths))

        if node.get_status() != Cell.NORMAL:
            node.set_status(Cell.ANALYZING)
        target.set_status(Cell.FOLLOWING)

        # We're still generating
        return True

class BreadthFirstSolver:
    def __init__(self, maze):
        self.maze = maze

        self.start    = maze.get_start()
        self.end      = maze.get_end()

        self.width    = self.maze.get_width()
        self.height   = self.maze.get_height()

        self.frontier = Queue()
        self.frontier.put(self.start)
        self.finished = False

        self.path = LifoQueue()

    def gen_path(self):
        x = self.end[0]
        y = self.end[1]
        self.path.put((x,y))

        while x!= self.start[0] or y != self.start[1]:
            tile = self.maze.get_tile(x, y)

            if not tile.has_route():
                return False
            direction = tile.get_route()
            x += direction[0]
            y += direction[1]
            self.path.put((x,y))

    def step(self):
        if self.frontier.empty() or self.finished:
            return False

        current = self.frontier.get()
        x    = current[0]
        y    = current[1]
        tile = self.maze.get_tile(x,y)
        tile.set_status(Cell.ANALYZING)

        if current[0] == self.end[0] and current[1] == self.end[1]:
            self.finished = True
            self.gen_path()
            return False

        paths = tile.get_paths()
        for path in paths:
            x2 = x+path[0]
            y2 = y+path[1]
            tile = self.maze.get_tile(x2, y2)
            if not tile.has_route():
                self.frontier.put((x2,y2))
                tile.set_route((-path[0], -path[1]))
        return True

    def solve(self):
        while True:
            if not self.step():
                return

    def trace_path(self):
        while True:
            if not self.trace_path_step():
                return

    def trace_path_step(self):
        if self.path.empty():
            return False
        pos = self.path.get()
        tile = self.maze.get_tile(*pos)
        tile.set_status(Cell.FOLLOWING)
        return True

class AStarSolver:

    def __init__(self, maze):
        self.maze = maze

        self.start   = maze.get_start()
        self.end     = maze.get_end()

        self.width   = self.maze.get_width()
        self.height  = self.maze.get_height()

        self.closed  = []
        self.open    = [self.start]
        self.path    = []

        self.finished = False

        # Scores for each of the places we'll visit during our exploration
        inf = (self.width+self.height + 1)**4
        self.scores = [
            [CellScore(inf, inf) for i in range(self.width)]
            for j in range(self.height)
        ]

        x = self.start[0]
        y = self.start[1]

        score = self.compute_cost(x,y)
        self.scores[y][x].set_gscore(0)
        self.scores[y][x].set_fscore(score)

    def is_closed(self, x, y):
        for node in self.closed:
            if node[0] == x and node[1]==y:
                return True
        return False

    def is_open(self, x, y):
        for node in self.open:
            if node[0] == x and node[1]==y:
                return True
        return False

    def solve(self):
        while True:
            if not self.step():
                return

    def step(self):
        #for row in self.scores:
        #    values = [col.get_gscore() for col in row]
        #    print(values)
        if self.finished or len(self.open) == 0:
            return not self.finished

        # Find node with the lowest F-Score
        current = self.open[0]
        idx = 0
        for i in range(1,len(self.open)):
            n = self.open[i]
            if self.scores[n[1]][n[0]].get_fscore() < self.scores[current[1]][current[0]].get_fscore():
                current = n
                idx = i
        # Remove current from open list and add to closed list
        self.open.pop(idx)
        self.closed.append(current)

        # Check if we're done
        if current[0]==self.end[0] and current[1] == self.end[1]:
            self.finished = True
            self.trace_solution()
            return not self.finished

        # Find each neighbour of the current node and evaluate it
        x = current[0]
        y = current[1]
        tile = self.maze.get_tile(x, y)
        tile.set_status(Cell.ANALYZING)
        for path in tile.get_paths():
            x2 = x + path[0]
            y2 = y + path[1]
            if not self.is_closed(x2, y2):
                gscore = self.scores[y][x].get_gscore() + self.manhattan_dist(x,y,x2,y2)
                if not self.is_open(x2,y2):
                    self.open.append((x2,y2))
                elif gscore >= self.scores[y2][x2].get_gscore():
                    continue
                self.scores[y2][x2].set_path(-path[0], -path[1])
                self.scores[y2][x2].set_gscore(gscore)
                fscore = gscore + self.compute_cost(x2,y2)
                self.scores[y2][x2].set_fscore(fscore)

        return True

    def trace_solution(self):
        print(self.scores[self.end[1]][self.end[0]].get_path())
        return

    def manhattan_dist(self, x1, y1, x2, y2):
        return abs(x2-x1) + abs(y2-y1)

    def compute_cost(self, x, y):
        print( self.manhattan_dist(x,y, *self.end), x,y,*self.end)
        return self.manhattan_dist(x,y, *self.end)
