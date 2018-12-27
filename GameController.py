import pygame, time, math
import Maze, Pacman, Pellet, RedGhost, PinkGhost, BlueGhost, OrangeGhost, LevelOne, LevelTwo

block_size = 32
size_of_grid = [19, 21]
pelletImage = pygame.image.load("Images/Pellet.bmp")
redTargetImage = pygame.image.load("Images/RedTarget.bmp")
pinkTargetImage = pygame.image.load("Images/PinkTarget.bmp")
blueTargetImage = pygame.image.load("Images/BlueTarget.bmp")
orangeTargetImage = pygame.image.load("Images/OrangeTarget.bmp")

blockNSE = pygame.image.load("Images/BlockNSE.bmp")
blockNSW = pygame.image.load("Images/BlockNSW.bmp")
blockNEW = pygame.image.load("Images/BlockNEW.bmp")
blockSEW = pygame.image.load("Images/BlockSEW.bmp")
blockSE = pygame.image.load("Images/BlockSE.bmp")
blockSW = pygame.image.load("Images/BlockSW.bmp")
blockNS = pygame.image.load("Images/BlockNS.bmp")
blockNW = pygame.image.load("Images/BlockNW.bmp")
blockNE = pygame.image.load("Images/BlockNE.bmp")
blockEW = pygame.image.load("Images/BlockEW.bmp")
blockN = pygame.image.load("Images/BlockN.bmp")
blockS = pygame.image.load("Images/BlockS.bmp")
blockE = pygame.image.load("Images/BlockE.bmp")
blockW = pygame.image.load("Images/BlockW.bmp")
emptyBlock = pygame.image.load("Images/EmptyBlock.bmp")


redTargetImage.set_colorkey((0, 0, 0))
pinkTargetImage.set_colorkey((0, 0, 0))
blueTargetImage.set_colorkey((0, 0, 0))
orangeTargetImage.set_colorkey((0, 0, 0))

chaseInterval = 20
scatterInterval = 7

max_level = 2

class GameController(object):


    def __init__(self, AI_Player):
        self.ghosts_playing = True
        self.Jarvis = AI_Player
        self.AI_playing = False
        if self.Jarvis is not None:
            self.AI_playing = True
        self.game_setup()

        self.start_game()


    def game_setup(self):
        pygame.init()

        self.lives = 3
        self.level = LevelOne.LevelOne()
        pygame.font.init()
        self.screen_font = pygame.font.SysFont('Comic Sans MS', 12)

        size = [a*block_size for a in size_of_grid]
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("My Computer Learns Pacman")

        self.last_direction = "E"
        self.pacman_position_changed = False
        self.ghost_position_changed = [False, False, False, False]
        self.playing_game = True
        self.score = 0
        self.clock = pygame.time.Clock()

        self.level_setup()

    def level_setup(self):
        self.level_beaten = False
        self.last_score_increase = time.time()
        self.last_position_change = time.time()
        self.start_time = time.time()
        self.scatter_start = time.time()
        self.chase_start = None
        self.scatter = True
        self.chase = False
        self.build_maze()
        self.add_pellets()

        self.reset_level()

    def reset_level(self):
        self.remove_pacman()
        self.remove_ghosts()
        self.add_pacman()
        self.cur_position = self.pacman.position
        self.add_ghosts()

    def remove_pacman(self):
        self.pacman = None

    def remove_ghosts(self):
        self.ghosts = []

    def build_maze(self):
        self.maze = self.level.maze
        self.cells = self.maze.list_cells()
        self.draw_blocks()
        pygame.display.update()

    def add_pellets(self):
        self.pellets = []
        self.pellet_positions = []
        for cell in self.cells:
            if not cell.is_block() and not cell.position in self.maze.no_pellet_positions:
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
        for b in self.maze.get_block_images():
            self.screen.blit(b[0], b[1])

    def draw_background(self):
        self.screen.fill((0, 0, 0))

    def draw_text(self):

        score_surface = self.screen_font.render('Score: %s' % self.score, False, (255,255,255))
        self.screen.blit(score_surface, (5, 5))

        for i in range(self.lives - 1):
            self.screen.blit(self.pacman.images[0], (block_size, block_size*(8+i*1.1)))

        if self.AI_playing:
            gen_surface = self.screen_font.render('Gen: %s' % self.Jarvis.gen, False, (255,255,255))
            num_surface = self.screen_font.render('Num: %s' % self.Jarvis.num, False, (255,255,255))

            self.screen.blit(gen_surface, (165, 5))
            self.screen.blit(num_surface, (300, 5))

        
    def update_ghosts(self):
        if not self.ghosts_playing:
            return
        self.update_ghost_mode()
        for i, g in enumerate(self.ghosts):
            if not g.active:
                g.try_to_activate(self.total_pellets - len(self.pellet_positions))
            g.update_direction()
            cur_screen_x = g.get_screen_x()
            cur_screen_y = g.get_screen_y()
            new_screen_x = g.get_screen_x()
            new_screen_y = g.get_screen_y()
            if g.direction == "N":
                new_screen_y = cur_screen_y - g.speed
            elif g.direction == "S":
                new_screen_y = cur_screen_y + g.speed
            elif g.direction == "E":
                new_screen_x = cur_screen_x + g.speed
            elif g.direction == "W":
                new_screen_x = cur_screen_x - g.speed

            if self.position_changed(cur_screen_x, cur_screen_y, new_screen_x, new_screen_y):
                new_screen_x = block_size * round(new_screen_x / block_size)
                new_screen_y = block_size * round(new_screen_y / block_size)
                g.set_position(int(new_screen_x / block_size), int(new_screen_y / block_size))

            g.set_screen_position(new_screen_x, new_screen_y)
            self.screen.blit(g.get_cur_image(), (new_screen_x, new_screen_y))

                
    def draw_targets(self):
        self.screen.blit(redTargetImage, (self.ghosts[0].target_square[0]*block_size, self.ghosts[0].target_square[1]*block_size))
        self.screen.blit(pinkTargetImage, (self.ghosts[1].target_square[0]*block_size, self.ghosts[1].target_square[1]*block_size))
        self.screen.blit(blueTargetImage, (self.ghosts[2].target_square[0]*block_size, self.ghosts[2].target_square[1]*block_size))
        self.screen.blit(orangeTargetImage, (self.ghosts[3].target_square[0]*block_size, self.ghosts[3].target_square[1]*block_size))

    def update_ghost_mode(self):
        if not self.ghosts_playing:
            return
        if self.scatter:
            if time.time() - self.scatter_start > self.level.ghost_sequences[0][1]:
                self.chase_start = time.time()
                self.chase = True
                self.scatter = False
                for g in self.ghosts:
                    g.update_mode()
        elif self.chase:
            if time.time() - self.chase_start > self.level.ghost_sequences[0][0]:
                self.scatter_start = time.time()
                self.chase = False
                self.scatter = True
                for g in self.ghosts:
                    g.update_mode()

    def add_pacman(self):
        speed = self.level.pacman_speed
        if self.AI_playing:
            speed = 32
        self.pacman = Pacman.Pacman(9, 15, block_size, speed)
        self.screen.blit(self.pacman.get_cur_image(), (self.pacman.get_screen_x(), self.pacman.get_screen_y()))
        pygame.display.update()

    def add_ghosts(self):
        if not self.ghosts_playing:
            return
        self.ghosts = [RedGhost.RedGhost(9, 7, self.maze, self.level.ghost_speed, self.pacman, block_size),
                       PinkGhost.PinkGhost(9, 9, self.maze, self.level.ghost_speed, self.pacman, block_size)]
        self.ghosts.append(BlueGhost.BlueGhost(8, 9, self.maze, self.level.ghost_speed, self.pacman, block_size, self.ghosts[0]))
        self.ghosts.append(OrangeGhost.OrangeGhost(10, 9, self.maze, self.level.ghost_speed, self.pacman, block_size))

    def update_pacman(self):
        cur_screen_x = self.pacman.get_screen_x()
        cur_screen_y = self.pacman.get_screen_y()
        new_screen_x, new_screen_y = self.pacman.get_screen_x(), self.pacman.get_screen_y()
        legal_path = self.maze.is_path_legal(self.pacman.position[0], self.pacman.position[1], self.pacman.direction)
        if legal_path:
            if self.pacman.direction == "N":
                new_screen_y = cur_screen_y-self.pacman.speed
            elif self.pacman.direction == "S":
                new_screen_y = cur_screen_y + self.pacman.speed
            elif self.pacman.direction == "E":
                new_screen_x = cur_screen_x + self.pacman.speed
            elif self.pacman.direction == "W":
                new_screen_x = cur_screen_x - self.pacman.speed

        if self.position_changed(cur_screen_x, cur_screen_y, new_screen_x, new_screen_y):
            self.pacman_position_changed = True
            new_screen_x = block_size * round(new_screen_x/block_size)
            new_screen_y = block_size * round(new_screen_y/block_size)
            self.pacman.set_position(int(new_screen_x / block_size), int(new_screen_y / block_size))
        self.pacman.set_screen_position(new_screen_x, new_screen_y)

        pacmanImage = self.pacman.get_cur_image(legal_path)
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


    
    def position_changed(self, old_x, old_y, new_x, new_y):
        if new_x % block_size == 0 and new_y % block_size == 0:
            return True
        elif new_x > old_x and new_x % block_size < old_x % block_size and not old_x % block_size == 0:
            return True
        elif new_x < old_x and new_x % block_size > old_x % block_size and not old_x % block_size == 0:
            return True
        elif new_y > old_y and new_y % block_size < old_y % block_size and not old_y % block_size == 0:
            return True
        elif new_y < old_y and new_y % block_size > old_y % block_size and not old_y % block_size == 0:
            return True
        return False
        
    def draw_everything(self):
        self.draw_background()
        self.draw_blocks()
        self.draw_pellets()
        self.draw_text()
        self.update_ghosts()
        self.update_pacman()
        #self.draw_targets()

    def start_game(self):
        while self.playing_game:

            if len(self.pellet_positions) == 0:
                self.increment_level()

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

            self.check_for_death()

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

            self.clock.tick(30)

    def check_for_death(self):
        ghost_positions = [g.position for g in self.ghosts]
        if self.pacman.position in ghost_positions:
            self.reduce_lives()

    def reduce_lives(self):
        if self.lives > 1:
            self.lives -= 1
            time.sleep(2)
            self.reset_level()
        else:
            self.playing_game = False

    def increment_level(self):
        if self.level.number == max_level:
            self.playing_game = False
            return
        else:
            self.level = self.level.get_next_level()
            self.level_setup()

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

        if len(pellet_distances) > 0:
            p_one = pellet_distances[0]

            p_one_ew = p_one[0]
            p_one_ns = p_one[1]
        else:
            p_one_ew = 0
            p_one_ns = 0

        stimuli = g_one_ns, g_one_ew,  g_two_ns, g_two_ew, wN, wS, wE, wW, p_one_ns, p_one_ew
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