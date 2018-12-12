import random
from sklearn import neural_network

class Jarvis(object):

    def __init__(self):
        pass

    def select_random_key(self):
        directions = ["up", "down", "left", "right"]

        selection = random.randint(0, 3)

        return directions[selection]
