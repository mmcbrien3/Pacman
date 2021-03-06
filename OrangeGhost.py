import Ghost
import math, pygame

class OrangeGhost(Ghost.Ghost):

    def __init__(self, x, y, maze, speed, pacman, block_size):
        self.pellet_thresh = 60
        self.images = []
        self.image_count = 0
        for i in range(1, 4):
            self.images.append(pygame.image.load("Images/OrangeGhost_" + str(i) + ".bmp"))
            self.images[i - 1].set_colorkey((0, 0, 0))
        super(OrangeGhost, self).__init__(x, y, maze, speed, pacman, block_size)

    def get_chase_target_square(self):
        enemy_x = self.pacman.get_x()
        enemy_y = self.pacman.get_y()

        dist_to_enemy = math.sqrt((enemy_x - self.position[0]) ** 2 + (enemy_y - self.position[1]) ** 2)

        if dist_to_enemy >= 8:
            self.target_square = (enemy_x, enemy_y)
        else:
            self.target_square = self.get_scatter_target_square()

        return self.target_square

    def try_to_activate(self, pellets_collected):
        if pellets_collected >= self.pellet_thresh:
            self.active = True
            return True
        return False

    def set_scatter_square(self):
        self.scatter_square = (0, 20)