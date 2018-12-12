
class Cell(object):
    wall_pairs = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

    def __init__(self, x, y, walls):
        self.position = (x, y)
        self.walls = {'N': False, 'S': False, 'E': False, 'W': False}
        for wall in walls:
            self.walls[wall] = True

    def get_x(self):
        return self.position[0]

    def get_y(self):
        return self.position[1]

    def is_block(self):
        if all(self.walls.values()):
            return True
        return False

