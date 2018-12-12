
class Pellet(object):

    def __init__(self, x, y, block_size):
        self.position = (x, y)
        self.screen_position = (block_size*x, block_size*y)
        self.eaten = False