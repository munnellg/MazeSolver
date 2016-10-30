import pygame
from app.maze import Maze, Cell, DepthFirstSearchGenerator, AStarSolver

class Screen:

    def __init__(self):
        self.width     = 800  # Set screen width
        self.height    = 600  # Set screen height
        self.cell_size = 4    # Determine the size of a cell on screen

        self.title = "Maze Solver"
        # Create a new game of life that will fit inside our window
        self.maze = Maze(
            self.width//(self.cell_size*2),
            self.height//(self.cell_size*2)
        )
        self.generator = DepthFirstSearchGenerator(self.maze)
        self.solver    = AStarSolver(self.maze)
        self.skip = False

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
        if self.skip:
            self.generator.generate()
            self.skip = False
        else:
            self.generator.step()

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
