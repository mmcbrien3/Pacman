import Ghost
import pygame

class RedGhost(Ghost.Ghost):

    def __init__(self, x, y, maze, speed, pacman, block_size):
        self.images = []
        self.image_count = 0
        for i in range(1, 4):
            self.images.append(pygame.image.load("Images/RedGhost_" + str(i) + ".bmp"))
            self.images[i - 1].set_colorkey((0, 0, 0))
        super(RedGhost, self).__init__(x, y, maze, speed, pacman, block_size)

    def get_chase_target_square(self):
        enemy_x = self.pacman.get_x()
        enemy_y = self.pacman.get_y()
        self.target_square = enemy_x, enemy_y
        return (enemy_x, enemy_y)

    def try_to_activate(self, pellets_collected):
        self.active = True
        return True

    def set_scatter_square(self):
        self.scatter_square = (18, 0)
