
class Pacman(object):

    def __init__(self, x, y, block_size, speed):
        self.position = (x, y)
        self.block_size = block_size
        self.screen_position = [a * block_size for a in self.position]
        self.speed = speed
        self.direction = "E"

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
