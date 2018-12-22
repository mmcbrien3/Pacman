import Ghost
import pygame

class PinkGhost(Ghost.Ghost):

    def __init__(self, x, y, maze, speed, pacman, block_size):
        self.images = []
        self.image_count = 0
        for i in range(1, 4):
            self.images.append(pygame.image.load("Images/PinkGhost_" + str(i) + ".bmp"))
            self.images[i - 1].set_colorkey((0, 0, 0))
        super(PinkGhost, self).__init__(x, y, maze, speed, pacman, block_size)

    def get_chase_target_square(self):
        enemy_x = self.pacman.get_x()
        enemy_y = self.pacman.get_y()
        enemy_dir = self.pacman.direction
        
        target_x = enemy_x
        target_y = enemy_y
        if enemy_dir == "N":
            target_y -= 3
        elif enemy_dir == "S":
            target_y += 3
        elif enemy_dir == "E":
            target_x += 3
        elif enemy_dir == "W":
            target_x -= 3

        self.target_square = (target_x, target_y)
        return self.target_square

    def try_to_activate(self, pellets_collected):
        self.active = True
        return True

    def set_scatter_square(self):
        self.scatter_square = (0, 0)