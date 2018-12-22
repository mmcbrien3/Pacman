import Ghost
import pygame

class BlueGhost(Ghost.Ghost):

    def __init__(self, x, y, maze, speed, pacman, block_size, red_ghost):
        self.red_ghost = red_ghost
        self.pellet_thresh = 30
        self.images = []
        self.image_count = 0
        for i in range(1, 4):
            self.images.append(pygame.image.load("Images/BlueGhost_" + str(i) + ".bmp"))
            self.images[i - 1].set_colorkey((0, 0, 0))
        super(BlueGhost, self).__init__(x, y, maze, speed, pacman, block_size)

    def get_chase_target_square(self):
        red_ghost_x, red_ghost_y = self.red_ghost.position[0], self.red_ghost.position[1]
        enemy_x = self.pacman.get_x()
        enemy_y = self.pacman.get_y()
        enemy_dir = self.pacman.direction
        
        future_enemy_x = enemy_x
        future_enemy_y = enemy_y
        if enemy_dir == "N":
            future_enemy_y -= 2
        elif enemy_dir == "S":
            future_enemy_y += 2
        elif enemy_dir == "E":
            future_enemy_x += 2
        elif enemy_dir == "W":
            future_enemy_x += 2

        red_enemy_diff_y = future_enemy_y - red_ghost_y
        red_enemy_diff_x = future_enemy_x - red_ghost_x

        red_enemy_diff_x *= 2
        red_enemy_diff_y *= 2

        self.target_square = (red_enemy_diff_x + red_ghost_x, red_enemy_diff_y + red_ghost_y)
        return self.target_square

    def try_to_activate(self, pellets_collected):
        if pellets_collected >= self.pellet_thresh:
            self.active = True
            return True
        return False


    def set_scatter_square(self):
        self.scatter_square = (18, 20)