import pygame
import Maze, Pacman, Pellet, Jarvis

AI_playing = True
block_size = 32
size_of_grid = [19, 21]
blockImage = pygame.image.load("Images/Block.png")
pacmanImage = pygame.image.load("Images/Pacman.png")
pelletImage = pygame.image.load("Images/Pellet.png")
pacmanImage.set_colorkey((0, 0, 0))

no_pellet_positions = ((8, 6), (10, 6),

                       (6, 7), (7, 7), (8, 7), (9, 7),
                       (10, 7), (11, 7), (12, 7),

                       (6, 8), (9, 8), (12, 8),

                       (6, 10), (12, 10),

                       (6, 11), (7, 11), (8, 11), (9, 11),
                       (10, 11), (11, 11), (12,11),

                       (6, 12), (12, 12),

                       (0, 9), (1, 9), (2, 9), (3, 9),
                       (5, 9), (6, 9), (8, 9), (9, 9),
                       (10, 9), (12, 9), (13, 9), (15, 9),
                       (16, 9), (17, 9), (18, 9))

class GameController(object):


    def __init__(self):
        self.setup()
        self.build_maze()
        self.add_pellets()
        self.add_pacman()
        self.add_ghosts()
        self.setup_AI()
        self.start_game()

    def setup(self):
        pygame.init()

        size = [a*32 for a in size_of_grid]
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("My Computer Learns Pacman")

        self.pacman_position_changed = False
        self.ghost_position_changed = [False, False, False, False]
        self.playing_game = True
        self.score = 0

        self.clock = pygame.time.Clock()

    def setup_AI(self):
        self.Jarvis = Jarvis.Jarvis()

    def build_maze(self):
        self.maze = Maze.Maze(size_of_grid[0], size_of_grid[1])
        self.cells = self.maze.list_cells()
        self.draw_blocks()
        pygame.display.update()

    def add_pellets(self):
        self.pellets = []
        self.pellet_positions = []
        for cell in self.cells:
            if not cell.is_block() and not cell.position in no_pellet_positions:
                self.pellets.append(Pellet.Pellet(cell.get_x(), cell.get_y(), block_size))
                self.pellet_positions.append((cell.get_x(), cell.get_y()))
        self.draw_pellets()
        pygame.display.update()

    def draw_pellets(self):
        for p in self.pellets:
            if p.position in self.pellet_positions:
                self.screen.blit(pelletImage, (p.screen_position[0], p.screen_position[1]))

    def draw_blocks(self):
        for cell in self.cells:
            if cell.is_block():
                screen_x = cell.get_x()*32
                screen_y = cell.get_y()*32
                self.screen.blit(blockImage, (screen_x, screen_y))

    def draw_background(self):
        self.screen.fill((0, 0, 0))

    def add_pacman(self):
        self.pacman = Pacman.Pacman(9, 15, block_size)
        self.screen.blit(pacmanImage, (self.pacman.get_screen_x(), self.pacman.get_screen_y()))
        pygame.display.update()

    def add_ghosts(self):
        pass

    def update_pacman(self):
        cur_screen_x = self.pacman.get_screen_x()
        cur_screen_y = self.pacman.get_screen_y()
        if self.pacman.direction == "N":
            cur_screen_y = cur_screen_y-self.pacman.speed
        elif self.pacman.direction == "S":
            cur_screen_y = cur_screen_y + self.pacman.speed
        elif self.pacman.direction == "E":
            cur_screen_x = cur_screen_x + self.pacman.speed
        elif self.pacman.direction == "W":
            cur_screen_x = cur_screen_x - self.pacman.speed

        self.pacman.set_screen_position(cur_screen_x, cur_screen_y)
        self.screen.blit(pacmanImage, (cur_screen_x, cur_screen_y))

        if cur_screen_x % 32 == 0 and cur_screen_y % 32 == 0:
            self.pacman_position_changed = True
            self.pacman.set_position(int(cur_screen_x / 32), int(cur_screen_y / 32))

    def draw_everything(self):
        self.draw_background()
        self.draw_blocks()
        self.draw_pellets()
        self.update_pacman()

    def start_game(self):
        while self.playing_game:

            if not AI_playing:
                self.read_keyboard_input()
            else:
                self.read_AI_input()
            self.draw_everything()

            if self.pacman_position_changed:
                if not self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), self.pacman.direction):
                    self.pacman.direction = ""
                self.pacman_position_changed = False
                if self.pacman.position in self.pellet_positions:
                    self.score += 10
                    self.pellet_positions.remove(self.pacman.position)

            pygame.display.update()
            pygame.event.pump()
            print(self.score)
            self.clock.tick(30)

    def read_keyboard_input(self):
        pressed_keys = pygame.key.get_pressed()
        in_center = self.pacman.get_screen_x() % 32 == 0 and self.pacman.get_screen_y() % 32 == 0
        if pressed_keys[pygame.K_LEFT]:
            if self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "W"):
                if self.pacman.direction == "E" or in_center:
                    self.pacman.set_direction("W")
        if pressed_keys[pygame.K_RIGHT]:
            if self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "E"):
                if self.pacman.direction == "W" or in_center:
                    self.pacman.set_direction("E")
        if pressed_keys[pygame.K_DOWN]:
            if self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "S"):
                if self.pacman.direction == "N" or in_center:
                    self.pacman.set_direction("S")
        if pressed_keys[pygame.K_UP]:
            if self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "N"):
                if self.pacman.direction == "S" or in_center:
                    self.pacman.set_direction("N")

    def read_AI_input(self):
        pressed_key = self.Jarvis.select_random_key()
        in_center = self.pacman.get_screen_x() % 32 == 0 and self.pacman.get_screen_y() % 32 == 0
        if pressed_key == "left":
            if self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "W"):
                if self.pacman.direction == "E" or in_center:
                    self.pacman.set_direction("W")
        if pressed_key == "right":
            if self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "E"):
                if self.pacman.direction == "W" or in_center:
                    self.pacman.set_direction("E")
        if pressed_key == "down":
            if self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "S"):
                if self.pacman.direction == "N" or in_center:
                    self.pacman.set_direction("S")
        if pressed_key == "up":
            if self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "N"):
                if self.pacman.direction == "S" or in_center:
                    self.pacman.set_direction("N")




GameController()