import pygame
from app.maze import Maze, Cell, DepthFirstSearchGenerator
from app.maze import AStarSolver, BreadthFirstSolver

class Screen:

    def __init__(self):
        self.width     = 1920  # Set screen width
        self.height    = 1080  # Set screen height
        self.cell_size = 4     # Determine the size of a cell on screen

        self.title = "Maze Solver"
        # Create a new game of life that will fit inside our window
        self.maze = Maze(
            self.width//(self.cell_size*2),
            self.height//(self.cell_size*2)
        )
        self.generator = DepthFirstSearchGenerator(self.maze)

        t = self.maze.get_tile(0,0)
        t.add_path((0,1))
        t.add_path((1,0))

        self.solver    = BreadthFirstSolver(self.maze)
        self.skip    = False
        self.solving = False
        self.tracing = False

    def draw_tile(self, surface, tile, x, y):
        if tile.get_status() == Cell.ANALYZING:
            colour = (255, 0, 0)
        elif tile.get_status() == Cell.FOLLOWING:
            colour = (0,255,0)
        else:
            colour = (255, 255, 255)

        pygame.draw.rect(
            surface,
            colour,
            (
                self.cell_size*x,
                self.cell_size*y,
                self.cell_size,
                self.cell_size
            )
        )

        if tile.get_status() == Cell.FOLLOWING:
            route = tile.get_route()
            pygame.draw.rect(
                surface,
                colour,
                (
                    self.cell_size*(x+route[0]),
                    self.cell_size*(y+route[1]),
                    self.cell_size,
                    self.cell_size
                )
            )
        else:
            for path in tile.get_paths():
                pygame.draw.rect(
                    surface,
                    colour,
                    (
                        self.cell_size*(x+path[0]),
                        self.cell_size*(y+path[1]),
                        self.cell_size,
                        self.cell_size
                    )
                )

    def render(self):
        # Create blank surface and fill with white
        surface = pygame.Surface((self.width, self.height))

        for y in range(1, (self.maze.get_height()*2), 2):
            for x in range(1, (self.maze.get_width()*2), 2):
                tile = self.maze.get_tile(x//2, y//2)
                if len(tile.get_paths()) > 0:
                    self.draw_tile(surface, tile, x, y)

        return surface

    def update(self):
        if self.tracing:
            if self.skip:
                self.solver.trace_path()
                self.skip = False
            else:
                self.solver.trace_path_step()
        elif self.solving:
            if self.skip:
                self.solver.solve()
                self.skip = False
                self.solving = True
            else:
                self.tracing = not self.solver.step()
        else:
            if self.skip:
                self.generator.generate()
                self.skip = False
            else:
                self.solving = not self.generator.step()

    def __game_loop(self):
        clock = pygame.time.Clock()
        pygame.mouse.set_visible(False)

        while True:
            # Regulate framerate
            clock.tick(60)

            # Check for any useful events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit() # player has quit the game
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.skip = True
                    elif event.key == pygame.K_ESCAPE:
                        self.quit()

            self.update()

            # Display the game state
            render = self.render()
            self.screen.blit(render, (0,0))
            pygame.display.flip()

    def __initialize_display(self):
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)

    def run(self):
        self.__initialize_display()
        self.__game_loop()

    def quit(self):
        exit()
