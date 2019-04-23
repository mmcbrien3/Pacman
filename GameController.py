import pygame, time, math, os, neat
import Maze, Pacman, Pellet, RedGhost, PinkGhost, BlueGhost, OrangeGhost, LevelOne, LevelTwo
import numpy as np
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
global GENERATION
GENERATION = 0
max_level = 2

class GameController(object):


    def __init__(self, genomes, config, gen):
        self.ghosts_playing = True
        self.AI_playing = False
        self.fr = 30
        if genomes is not None:
            self.AI_playing = True
            self.fr = 99999
            self.genomes = []
            for gid, genome in genomes:
                self.genomes.append(genome)
            self.config = config
            self.gen = gen
        self.game_setup()

    def game_setup(self):
        pygame.init()


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
        if not self.AI_playing:
            self.lives = [3]
        else:
            self.lives = [1] * len(self.pacman)

    def level_setup(self):
        self.build_maze()

        self.reset_level()

        self.level_beaten = False
        self.last_score_increase = time.time()
        self.last_position_change = time.time()
        self.start_time = time.time()
        self.scatter_start = time.time()
        self.chase_start = None
        self.scatter = True
        self.chase = False
        self.add_pellets()


    def reset_level(self):
        self.remove_pacman()
        self.remove_ghosts()
        self.add_pacman()
        self.cur_position = self.pacman[0].position
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
        for i in range(len(self.pacman)):
            self.pellets.append([])
            self.pellet_positions.append([])
            for cell in self.cells:
                if not cell.is_block() and not cell.position in self.maze.no_pellet_positions:
                    self.pellets[i].append(Pellet.Pellet(cell.get_x(), cell.get_y(), block_size))
                    self.pellet_positions[i].append((cell.get_x(), cell.get_y()))
        self.total_pellets = len(self.pellets[0])
        self.draw_pellets()
        pygame.display.update()

    def draw_pellets(self):
        p_alive = sum([1 for p in self.pacman if p.alive])
        if p_alive > 1:
            return
        for i in range(len(self.pacman)):
            if self.pacman[i].alive:
                for p in self.pellets[i]:
                    if p.position in self.pellet_positions[i]:
                        self.screen.blit(pelletImage, (p.screen_position[0], p.screen_position[1]))

    def draw_blocks(self):
        for b in self.maze.get_block_images():
            self.screen.blit(b[0], b[1])

    def draw_background(self):
        self.screen.fill((0, 0, 0))

    def draw_text(self):

        score_surface = self.screen_font.render('Score: %s' % self.score, False, (255,255,255))
        self.screen.blit(score_surface, (5, 5))

        if not self.AI_playing:
            for i in range(self.lives[0] - 1):
                self.screen.blit(self.pacman[0].images[0], (block_size, block_size*(8+i*1.1)))

        if self.AI_playing:
            gen_surface = self.screen_font.render('Gen: %s' % self.gen, False, (255,255,255))
            p_alive = sum([1 for p in self.pacman if p.alive])
            alive_surface = self.screen_font.render('Alive: %s' % p_alive, False, (255, 255, 255))
            best_score = max(self.scores)
            bs_surface = self.screen_font.render('Best Score: %s' % best_score, False, (255, 255, 255))
            self.screen.blit(gen_surface, (60, 5))
            self.screen.blit(alive_surface, (160, 5))
            self.screen.blit(bs_surface, (260, 5))


    def update_ghosts(self):
        if not self.ghosts_playing:
            return
        self.update_ghost_mode()
        c = 0
        for gs in self.ghosts:
            if not self.pacman[c].alive:
                c+=1
                continue
            c+=1
            for i, g in enumerate(gs):
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
                for gs in self.ghosts:
                    for g in gs:
                        g.update_mode()
        elif self.chase:
            if time.time() - self.chase_start > self.level.ghost_sequences[0][0]:
                self.scatter_start = time.time()
                self.chase = False
                self.scatter = True
                for gs in self.ghosts:
                    for g in gs:
                        g.update_mode()

    def add_pacman(self):
        speed = self.level.pacman_speed
        if not self.AI_playing:
            self.pacman = [Pacman.Pacman(9, 15, block_size, speed)]
        else:
            self.pacman = []
            self.networks = []
            for i in range(len(self.genomes)):
                self.pacman.append(Pacman.Pacman(9, 15, block_size, speed))
                net = neat.nn.FeedForwardNetwork.create(self.genomes[i], config)
                self.networks.append(net)
        self.scores = [0] * len(self.pacman)
        self.num_alive = len(self.pacman)
        for p in self.pacman:
            self.screen.blit(p.get_cur_image(), (p.get_screen_x(), p.get_screen_y()))
        pygame.display.update()

    def add_ghosts(self):
        if not self.ghosts_playing:
            return
        self.ghosts = []
        for i in range(len(self.pacman)):
            self.ghosts.append([])
            self.ghosts[i].extend([RedGhost.RedGhost(9, 7, self.maze, self.level.ghost_speed, self.pacman[i], block_size),
                       PinkGhost.PinkGhost(9, 9, self.maze, self.level.ghost_speed, self.pacman[i], block_size)])
            self.ghosts[i].append(BlueGhost.BlueGhost(8, 9, self.maze, self.level.ghost_speed, self.pacman[i], block_size, self.ghosts[i][0]))
            self.ghosts[i].append(OrangeGhost.OrangeGhost(10, 9, self.maze, self.level.ghost_speed, self.pacman[i], block_size))

    def update_pacman(self):
        for p in self.pacman:
            if not p.alive:
                continue
            cur_screen_x = p.get_screen_x()
            cur_screen_y = p.get_screen_y()
            new_screen_x, new_screen_y = p.get_screen_x(), p.get_screen_y()
            legal_path = self.maze.is_path_legal(p.position[0], p.position[1], p.direction)
            if legal_path:
                if p.direction == "N":
                    new_screen_y = cur_screen_y-p.speed
                elif p.direction == "S":
                    new_screen_y = cur_screen_y + p.speed
                elif p.direction == "E":
                    new_screen_x = cur_screen_x + p.speed
                elif p.direction == "W":
                    new_screen_x = cur_screen_x - p.speed

            if self.position_changed(cur_screen_x, cur_screen_y, new_screen_x, new_screen_y):
                p_position_changed = True
                new_screen_x = block_size * round(new_screen_x/block_size)
                new_screen_y = block_size * round(new_screen_y/block_size)
                p.set_position(int(new_screen_x / block_size), int(new_screen_y / block_size))
            p.set_screen_position(new_screen_x, new_screen_y)

            pacmanImage = p.get_cur_image(legal_path)
            if p.direction == "N":
                self.screen.blit(pygame.transform.rotate(pacmanImage, 90), (cur_screen_x, cur_screen_y))
            elif p.direction == "S":
                self.screen.blit(pygame.transform.rotate(pacmanImage, -90), (cur_screen_x, cur_screen_y))
            elif p.direction == "E":
                self.screen.blit(pacmanImage, (cur_screen_x, cur_screen_y))
            elif p.direction == "W":
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
                self.get_stimuli(self.pacman[0], 0)
            else:
                c = 0
                for p in self.pacman:
                    if p.alive:
                        self.read_AI_input(self.networks[c], p, c)
                    c+=1
            self.draw_everything()

            c = 0
            for p in self.pacman:
                if p.alive:
                    if not self.maze.is_path_legal(p.get_x(), p.get_y(), p.direction):
                        self.last_direction = p.direction
                    self.pacman_position_changed = False
                    if p.position in self.pellet_positions[c]:
                        self.scores[c] += 10
                        self.pellet_positions[c].remove(p.position)
                c += 1

            self.check_for_death()

            if not any(self.lives):
                self.playing_game = False
                return self.scores
            pygame.display.update()
            pygame.event.pump()

            time_since_last_score = time.time() - self.last_score_increase
            time_since_last_position_change = time.time() - self.last_position_change
            self.clock.tick(self.fr)

    def check_for_death(self):
        c = 0
        for p in self.pacman:
            if p.alive:
                cur_ghosts = self.ghosts[c]
                ghost_positions = [g.position for g in cur_ghosts]
                if p.position in ghost_positions:
                    self.reduce_lives(c)
            c += 1

    def reduce_lives(self, c):
        if self.lives[c] > 1:
            self.lives[c] -= 1
            if not self.AI_playing:
                self.reset_level()
        else:
            self.lives[c] = 0
            if not self.AI_playing:
                self.playing_game = False
            else:
                self.pacman[c].alive = False

    def increment_level(self):
        if self.level.number == max_level:
            self.playing_game = False
            return
        else:
            self.level = self.level.get_next_level()
            self.level_setup()

    def read_keyboard_input(self):
        p = self.pacman[0]
        self.input_to_print = p.direction
        pressed_keys = pygame.key.get_pressed()
        in_center = p.get_screen_x() % 32 == 0 and p.get_screen_y() % 32 == 0
        if pressed_keys[pygame.K_LEFT]:
            self.input_to_print = "W"
            if self.maze.is_path_legal(p.get_x(), p.get_y(), "W"):
                if p.direction == "E" or in_center:
                    p.set_direction("W")
        if pressed_keys[pygame.K_RIGHT]:
            self.input_to_print = "E"
            if self.maze.is_path_legal(p.get_x(), p.get_y(), "E"):
                if p.direction == "W" or in_center:
                    p.set_direction("E")
        if pressed_keys[pygame.K_DOWN]:
            self.input_to_print = "S"
            if self.maze.is_path_legal(p.get_x(), p.get_y(), "S"):
                if p.direction == "N" or in_center:
                    p.set_direction("S")
        if pressed_keys[pygame.K_UP]:
            self.input_to_print = "N"
            if self.maze.is_path_legal(p.get_x(), p.get_y(), "N"):
                if p.direction == "S" or in_center:
                    p.set_direction("N")

    def read_AI_input(self, net, p, c):
        if not self.maze.is_cell_critical(p.get_x(), p.get_y()):
            return
        s = self.get_stimuli(p, c)
        pressed_key = np.argmax(net.activate(s))
        in_center = p.get_screen_x() % 32 == 0 and p.get_screen_y() % 32 == 0
        if pressed_key == 1:
            if self.maze.is_path_legal(p.get_x(), p.get_y(), "W"):
                if p.direction == "E" or in_center:
                    p.set_direction("W")
        if pressed_key == 2:
            if self.maze.is_path_legal(p.get_x(), p.get_y(), "E"):
                if p.direction == "W" or in_center:
                    p.set_direction("E")
        if pressed_key == 3:
            if self.maze.is_path_legal(p.get_x(), p.get_y(), "S"):
                if p.direction == "N" or in_center:
                    p.set_direction("S")
        if pressed_key == 4:
            if self.maze.is_path_legal(p.get_x(), p.get_y(), "N"):
                if p.direction == "S" or in_center:
                    p.set_direction("N")


    def get_stimuli(self, p, c):

        g_one_ns, g_one_ew, g_two_ns, g_two_ew = 0, 0, 0, 0
        wN, wS, wE, wW = 0, 0, 0, 0
        pn, ps, pe, pw = 0, 0, 0, 0
        if not self.maze.is_path_legal(p.get_x(), p.get_y(), "N"):
            wN = 1
        if not self.maze.is_path_legal(p.get_x(), p.get_y(), "S"):
            wS = 1
        if not self.maze.is_path_legal(p.get_x(), p.get_y(), "E"):
            wE = 1
        if not self.maze.is_path_legal(p.get_x(), p.get_y(), "W"):
            wW = 1

        pellet_distances = self.get_pellet_distances(p.get_x(), p.get_y(), c)

        if len(pellet_distances) > 0:
            for p in pellet_distances:
                if p[0] >= 0:
                    pe = p[0]
                if p[0] <= 0:
                    pw = abs(p[0])
                if p[1] >= 0:
                    ps = p[1]
                if p[1] <= 0:
                    pn = abs(p[1])
        else:
            pn = -1
            ps = -1
            pe = -1
            pw = -1

        stimuli = wN, wS, wE, wW, pn, ps, pe, pw
        if c == 0:
            print(stimuli)
        return stimuli

    def get_pellet_distances(self, x, y, c):
        dists = []
        diff_dists = []
        min = 9999
        ind = -1
        for i, p in enumerate(self.pellet_positions[c]):
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
def eval_genomes(genomes, config):
    #i = 0
    global SCORE
    global GENERATION, MAX_FITNESS, BEST_GENOME

    GENERATION += 1
    #for genome_id, genome in genomes:
    c = GameController(genomes, config, GENERATION)
    scores = c.start_game()
    i = 0
    print(scores)
    for g_id, g in genomes:
        g.fitness = scores[i]
        i += 1

if __name__ == '__main__':
    learn_pacman = True
    if learn_pacman:
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             'config')
        pop = neat.Population(config)
        # stats = neat.StatisticsReporter()
        # pop.add_reporter(stats)

        winner = pop.run(eval_genomes, 300)

        print(winner)
    else:
        c = GameController(None, None, None)
        c.start_game()
