#!/usr/bin/env python3
import random

class Cell:
    NORMAL    = 0
    ANALYZING = 1
    FOLLOWING = 2

    def __init__(self, path):
        self.paths  = path
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
            string += "{}\n".format(line)
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
            if self.step() == False:
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

class AStarSolver:
    def __init__(self, maze):
        self.maze = maze

        self.start   = maze.get_start()
        self.end     = maze.get_end()
        
        self.current = self.start
        
        self.explored  = []
        self.exploring = [self.maze.get_tile(self.start[0], self.start[1])]
        self.path      = []

        # Scores for each of the places we'll visit during our exploration
        inf = self.maze.get_width()+self.maze.get_height() + 1
        self.scores = [
            [[inf, inf] for i in range(self.maze.get_width())] 
            for j in range(self.maze.get_height())
        ]
        
        self.scores[self.start[0]][self.start[1]][0] = 0
        self.scores[self.start[0]][self.start[1]][1] = self.compute_cost(self.start[0], self.start[1])

    def step(self):
        if self.current[0]==self.end[0] and self.current[1] == self.end[1]:
            return False

        
    def compute_cost(self, x, y):
        return abs(self.end[0]-x) + abs(self.end[1]-y)
