import pygame, time, math
import Maze, Pacman, Pellet, RedGhost, PinkGhost, BlueGhost, OrangeGhost

block_size = 32
size_of_grid = [19, 21]
blockImage = pygame.image.load("Images/Block.bmp")
pacmanImage = pygame.image.load("Images/Pacman.bmp")
pelletImage = pygame.image.load("Images/Pellet.bmp")
redGhostImage = pygame.image.load("Images/RedGhost.bmp")
pinkGhostImage = pygame.image.load("Images/PinkGhost.bmp")
blueGhostImage = pygame.image.load("Images/BlueGhost.bmp")
orangeGhostImage = pygame.image.load("Images/OrangeGhost.bmp")
redTargetImage = pygame.image.load("Images/RedTarget.bmp")
pinkTargetImage = pygame.image.load("Images/PinkTarget.bmp")
blueTargetImage = pygame.image.load("Images/BlueTarget.bmp")
orangeTargetImage = pygame.image.load("Images/OrangeTarget.bmp")

pacmanImage.set_colorkey((0, 0, 0))
redGhostImage.set_colorkey((0, 0, 0))
pinkGhostImage.set_colorkey((0, 0, 0))
blueGhostImage.set_colorkey((0, 0, 0))
orangeGhostImage.set_colorkey((0, 0, 0))
redTargetImage.set_colorkey((0, 0, 0))
pinkTargetImage.set_colorkey((0, 0, 0))
blueTargetImage.set_colorkey((0, 0, 0))
orangeTargetImage.set_colorkey((0, 0, 0))

print(redGhostImage.get_colorkey())
print(redTargetImage.get_colorkey())

chaseInterval = 5
scatterInterval = 3

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


    def __init__(self, AI_Player):
        self.Jarvis = AI_Player
        self.AI_playing = False
        if self.Jarvis is not None:
            self.AI_playing = True
        self.setup()
        self.build_maze()
        self.add_pellets()
        self.add_pacman()
        self.cur_position = self.pacman.position
        self.add_ghosts()
        self.start_game()


    def setup(self):
        pygame.init()

        pygame.font.init()
        self.screen_font = pygame.font.SysFont('Comic Sans MS', 12)

        size = [a*32 for a in size_of_grid]
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("My Computer Learns Pacman")

        self.last_direction = "E"
        self.pacman_position_changed = False
        self.ghost_position_changed = [False, False, False, False]
        self.playing_game = True
        self.score = 0
        self.last_score_increase = time.time()
        self.last_position_change = time.time()
        self.start_time = time.time()
        self.scatter_start = time.time()
        self.chase_start = None
        self.scatter = True
        self.chase = False


        self.clock = pygame.time.Clock()


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
        self.total_pellets = len(self.pellets)
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

    def draw_text(self):

        score_surface = self.screen_font.render('Score: %s' % self.score, False, (255,255,255))
        self.screen.blit(score_surface, (5, 5))

        if not self.AI_playing:
            return
        gen_surface = self.screen_font.render('Gen: %s' % self.Jarvis.gen, False, (255,255,255))
        num_surface = self.screen_font.render('Num: %s' % self.Jarvis.num, False, (255,255,255))

        self.screen.blit(gen_surface, (165, 5))
        self.screen.blit(num_surface, (300, 5))
        
    def update_ghosts(self):
        self.update_ghost_mode()
        for i, g in enumerate(self.ghosts):
            if not g.active:
                g.try_to_activate(self.total_pellets - len(self.pellet_positions))
            g.update_direction()
            cur_screen_x = g.get_screen_x()
            cur_screen_y = g.get_screen_y()
            if g.direction == "N":
                cur_screen_y = cur_screen_y - g.speed
            elif g.direction == "S":
                cur_screen_y = cur_screen_y + g.speed
            elif g.direction == "E":
                cur_screen_x = cur_screen_x + g.speed
            elif g.direction == "W":
                cur_screen_x = cur_screen_x - g.speed

            g.set_screen_position(cur_screen_x, cur_screen_y)
            self.screen.blit(self.ghost_images[i], (cur_screen_x, cur_screen_y))

            if self.position_changed(cur_screen_x, cur_screen_y):
                g.set_position(int(cur_screen_x / 32), int(cur_screen_y / 32))
                
    def draw_targets(self):
        self.screen.blit(redTargetImage, (self.ghosts[0].target_square[0]*block_size, self.ghosts[0].target_square[1]*block_size))
        self.screen.blit(pinkTargetImage, (self.ghosts[1].target_square[0]*block_size, self.ghosts[1].target_square[1]*block_size))
        self.screen.blit(blueTargetImage, (self.ghosts[2].target_square[0]*block_size, self.ghosts[2].target_square[1]*block_size))
        self.screen.blit(orangeTargetImage, (self.ghosts[3].target_square[0]*block_size, self.ghosts[3].target_square[1]*block_size))

    def update_ghost_mode(self):
        if self.scatter:
            if time.time() - self.scatter_start > scatterInterval:
                self.chase_start = time.time()
                self.chase = True
                self.scatter = False
                for g in self.ghosts:
                    g.update_mode()
        elif self.chase:
            if time.time() - self.chase_start > chaseInterval:
                self.scatter_start = time.time()
                self.chase = False
                self.scatter = True
                for g in self.ghosts:
                    g.update_mode()



    def add_pacman(self):
        speed = 4
        if self.AI_playing:
            speed = 32
        self.pacman = Pacman.Pacman(9, 15, block_size, speed)
        self.screen.blit(pacmanImage, (self.pacman.get_screen_x(), self.pacman.get_screen_y()))
        pygame.display.update()

    def add_ghosts(self):
        self.ghosts = [RedGhost.RedGhost(9, 7, self.maze, 4, self.pacman, block_size),
                       PinkGhost.PinkGhost(9, 9, self.maze, 4, self.pacman, block_size)]
        self.ghosts.append(BlueGhost.BlueGhost(8, 9, self.maze, 4, self.pacman, block_size, self.ghosts[0]))
        self.ghosts.append(OrangeGhost.OrangeGhost(10, 9, self.maze, 4, self.pacman, block_size))
        self.ghost_images = [redGhostImage, pinkGhostImage, blueGhostImage, orangeGhostImage]
        pass

    def update_pacman(self):
        cur_screen_x = self.pacman.get_screen_x()
        cur_screen_y = self.pacman.get_screen_y()
        if self.maze.is_path_legal(self.pacman.position[0], self.pacman.position[1], self.pacman.direction):
            if self.pacman.direction == "N":
                cur_screen_y = cur_screen_y-self.pacman.speed
            elif self.pacman.direction == "S":
                cur_screen_y = cur_screen_y + self.pacman.speed
            elif self.pacman.direction == "E":
                cur_screen_x = cur_screen_x + self.pacman.speed
            elif self.pacman.direction == "W":
                cur_screen_x = cur_screen_x - self.pacman.speed

        self.pacman.set_screen_position(cur_screen_x, cur_screen_y)

        if self.pacman.direction == "N":
            self.screen.blit(pygame.transform.rotate(pacmanImage, 90), (cur_screen_x, cur_screen_y))
        elif self.pacman.direction == "S":
            self.screen.blit(pygame.transform.rotate(pacmanImage, -90), (cur_screen_x, cur_screen_y))
        elif self.pacman.direction == "E":
            self.screen.blit(pacmanImage, (cur_screen_x, cur_screen_y))
        elif self.pacman.direction == "W":
            self.screen.blit(pygame.transform.rotate(pacmanImage, 180), (cur_screen_x, cur_screen_y))
        else:
            if self.last_direction == "N":
                self.screen.blit(pygame.transform.rotate(pacmanImage, 90), (cur_screen_x, cur_screen_y))
            elif self.last_direction == "S":
                self.screen.blit(pygame.transform.rotate(pacmanImage, -90), (cur_screen_x, cur_screen_y))
            elif self.last_direction == "E":
                self.screen.blit(pacmanImage, (cur_screen_x, cur_screen_y))
            elif self.last_direction == "W":
                self.screen.blit(pygame.transform.rotate(pacmanImage, 180), (cur_screen_x, cur_screen_y))

        if self.position_changed(cur_screen_x, cur_screen_y):
            self.pacman_position_changed = True
            self.pacman.set_position(int(cur_screen_x / 32), int(cur_screen_y / 32))
    
    def position_changed(self, x, y):
        if x % 32 == 0 and y % 32 == 0:
            return True
        else:
            return False
        
    def draw_everything(self):
        self.draw_background()
        self.draw_blocks()
        self.draw_pellets()
        self.draw_text()
        self.update_ghosts()
        self.update_pacman()
        self.draw_targets()

    def start_game(self):
        while self.playing_game:

            if not self.AI_playing:
                self.read_keyboard_input()
            else:
                inputs = self.get_AI_inputs()
                self.Jarvis.set_inputs((inputs))
                self.read_AI_input()
            self.draw_everything()

            if self.pacman_position_changed:
                if not self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), self.pacman.direction):
                    self.last_direction = self.pacman.direction
                self.pacman_position_changed = False
                if self.pacman.position in self.pellet_positions:
                    self.score += 10
                    self.last_score_increase = time.time()
                    self.pellet_positions.remove(self.pacman.position)

            pygame.display.update()
            pygame.event.pump()

            time_since_last_score = time.time() - self.last_score_increase
            time_since_last_position_change = time.time() - self.last_position_change
            if self.AI_playing:
                if time_since_last_score > 2 or time_since_last_position_change > 0.2:
                    self.playing_game = False
                    self.Jarvis.end_game(self.score)
                if not self.pacman.position == self.cur_position:
                    self.cur_position = self.pacman.position
                    self.last_position_change = time.time()

            if not self.AI_playing:
                data_file = open(r".\dataFile.txt", "a")
                data_file.writelines(self.input_to_print + "\n")
                data_file.writelines(str(self.get_AI_inputs()) + "\n")
                data_file.close()


            self.clock.tick(30)

    def read_keyboard_input(self):
        self.input_to_print = self.pacman.direction
        pressed_keys = pygame.key.get_pressed()
        in_center = self.pacman.get_screen_x() % 32 == 0 and self.pacman.get_screen_y() % 32 == 0
        if pressed_keys[pygame.K_LEFT]:
            self.input_to_print = "W"
            if self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "W"):
                if self.pacman.direction == "E" or in_center:
                    self.pacman.set_direction("W")
        if pressed_keys[pygame.K_RIGHT]:
            self.input_to_print = "E"
            if self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "E"):
                if self.pacman.direction == "W" or in_center:
                    self.pacman.set_direction("E")
        if pressed_keys[pygame.K_DOWN]:
            self.input_to_print = "S"
            if self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "S"):
                if self.pacman.direction == "N" or in_center:
                    self.pacman.set_direction("S")
        if pressed_keys[pygame.K_UP]:
            self.input_to_print = "N"
            if self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "N"):
                if self.pacman.direction == "S" or in_center:
                    self.pacman.set_direction("N")

    def read_AI_input(self):
        if not self.maze.is_cell_critical(self.pacman.get_x(), self.pacman.get_y()):
            return
        pressed_key = self.Jarvis.select_key_from_net()
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

                    
    def get_AI_inputs(self):

        g_one_ns, g_one_ew,  g_two_ns, g_two_ew = 0, 0, 0, 0
        wN, wS, wE, wW = 0, 0, 0, 0
        p_one_ns, p_one_ew = 0, 0
        if not self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "N"):
            wN = 1
        if not self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "S"):
            wS = 1
        if not self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "E"):
            wE = 1
        if not self.maze.is_path_legal(self.pacman.get_x(), self.pacman.get_y(), "W"):
            wW = 1

        pellet_distances = self.get_pellet_distances(self.pacman.get_x(), self.pacman.get_y())

        p_one = pellet_distances[0]

        p_one_ew = p_one[0]
        p_one_ns = p_one[1]

        stimuli = g_one_ns, g_one_ew,  g_two_ns, g_two_ew, wN, wS, wE, wW, p_one_ns, p_one_ew
        print(stimuli)
        return stimuli

    def get_pellet_distances(self, x, y):
        dists = []
        diff_dists = []
        min = 9999
        ind = -1
        for i, p in enumerate(self.pellet_positions):
            dist = math.sqrt((p[0] - x) ** 2 + (p[1] - y) ** 2)
            dists.append(dist)
            diff_dists.append((p[0]-x, p[1] - y))
        return [x for _,x in sorted(zip(dists,diff_dists))]


    def is_pellet_in_direction(self, x, y, direction):
        if direction == "N":
            if (x, y - 1) in self.pellet_positions:
                return 1
            else:
                if self.maze.is_path_legal(x, y, "N"):
                    dist = self.is_pellet_in_direction(x, y + 1, "N")
                    return 1 + dist if not dist == -1 else -1
                else:
                    return -1
        elif direction == "S":
            if (x, y + 1) in self.pellet_positions:
                return 1
            else:
                if self.maze.is_path_legal(x, y, "S"):
                    dist = self.is_pellet_in_direction(x, y - 1, "S")
                    return 1 + dist if not dist == -1 else -1
                else:
                    return -1
        elif direction == "E":
            if (x + 1, y) in self.pellet_positions:
                return 1
            else:
                if self.maze.is_path_legal(x, y, "E"):
                    dist = self.is_pellet_in_direction(x + 1, y, "E")
                    return 1 + dist if not dist == -1 else -1
                else:
                    return -1
        elif direction == "W":
            if (x - 1, y) in self.pellet_positions:
                return 1
            else:
                if self.maze.is_path_legal(x, y, "W"):
                    dist = self.is_pellet_in_direction(x - 1, y, "W")
                    return 1 + dist if not dist == -1 else -1
                else:
                    return -1

    def distance_to_pellet(self, x, y, direction, visited):
        og_visited = visited[:]
        if (x, y) in self.pellet_positions:
            return 1
        else:
            directions = self.maze.get_legal_directions(x, y)
            if len(directions) == 0:
                return 9999
            northDir, southDir, eastDir, westDir = 9999,9999,9999,9999
            for dir in directions:
                if dir == "N" and not (x, y-1) in visited:
                    visited.append((x, y-1))
                    northDir = min(self.distance_to_pellet(x, y - 1, "N", visited), self.distance_to_pellet(x, y - 1, "S", visited),
                                   self.distance_to_pellet(x, y - 1, "E", visited), self.distance_to_pellet(x, y - 1, "W", visited))
                    visited = og_visited
                elif dir == "S" and not (x, y + 1) in visited:
                    visited.append((x, y + 1))
                    southDir = min(self.distance_to_pellet(x, y + 1, "N", visited), self.distance_to_pellet(x, y + 1, "S", visited),
                                   self.distance_to_pellet(x, y + 1, "E", visited), self.distance_to_pellet(x, y + 1, "W", visited))
                    visited = og_visited
                elif dir == "E" and not (x + 1, y) in visited:
                    visited.append((x + 1, y))
                    eastDir = min(self.distance_to_pellet(x + 1, y, "N", visited), self.distance_to_pellet(x + 1, y, "S", visited),
                                   self.distance_to_pellet(x + 1, y, "E", visited), self.distance_to_pellet(x + 1, y, "W", visited))
                    visited = og_visited
                elif dir == "W" and not (x - 1, y) in visited:
                    visited.append((x - 1, y))
                    westDir = min(self.distance_to_pellet(x - 1, y, "N", visited), self.distance_to_pellet(x - 1, y, "S", visited),
                                   self.distance_to_pellet(x - 1, y, "E", visited), self.distance_to_pellet(x - 1, y, "W", visited))
                    visited = og_visited
            return min(northDir, southDir, eastDir, westDir) + 1

if __name__ == '__main__':
    GameController(None)