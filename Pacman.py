import pygame

class Pacman(object):

    def __init__(self, x, y, block_size, speed):
        self.position = (x, y)
        self.block_size = block_size
        self.screen_position = [a * block_size for a in self.position]
        self.speed = speed
        self.direction = "E"
        self.images = []
        self.image_count = 0
        for i in range(1, 6):
            self.images.append(pygame.image.load("Images/Pacman_" + str(i) + ".bmp"))
            self.images[i-1].set_colorkey((0, 0, 0))

    def get_cur_image(self, update=True):
        if not update:
            return self.images[self.image_count]

        if self.image_count + 1 < len(self.images):
            self.image_count += 1
        else:
            self.image_count = 0
        return self.images[self.image_count]

    def get_x(self):
        return self.position[0]

    def get_y(self):
        return self.position[1]

    def get_screen_x(self):
        return self.screen_position[0]

    def get_screen_y(self):
        return self.screen_position[1]

    def set_position(self, x, y):
        self.position = (x, y)

    def set_screen_position(self, x, y):
        self.screen_position = (x, y)

    def set_direction(self, dir):
        self.direction = dir
