import random
from sklearn.neural_network import MLPClassifier
import MLPClassifierManualSetup
from sklearn.preprocessing import LabelBinarizer


''' 
Inputs into net:
    Distance to ghost in each direction     (4)
    Current amount of points                (1)
    Distance to pellet in each direction    (4)
    Existence of wall in each direction     (4)
'''
def get_initial_data():
    with open("dataFile.txt") as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    directions = content[0:len(content):2]
    inputs = content[1:len(content):2]
    inputs = [eval(i) for i in inputs]
    for i in range(len(directions)):
        if directions[i] == "N":
            directions[i] = "up"
        elif directions[i] == "S":
            directions[i] = "down"
        elif directions[i] == "E":
            directions[i] = "right"
        elif directions[i] == "W":
            directions[i] = "left"
    return (directions, inputs)

directions = ["left", "right", "up", "down"]
inputs = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

class Jarvis(object):

    def __init__(self, gen, num, layers, coefs=None, intercepts=None):
        self.gen = gen
        self.num = num
        self.layers = layers
        self.final_score = 0
        self.setup_net(coefs, intercepts)
        self.game_ended = False

    def start_game(self):
        import GameController
        GameController.GameController(self)

    #gN, gS, gE, gW, pN, pS, pE, pW, wN, wS, wE, wW
    def set_inputs(self, inputs):
        self.inputs = inputs

    def setup_net(self, coefs=None, intercepts=None):
        if coefs is None:
            print("random nn")
            self.net = MLPClassifier(hidden_layer_sizes=self.layers)
            self.net.fit(inputs, directions)
            print(self.net.intercepts_)
        else:
            original_coefs = coefs
            print("pre trained nn")
            self.net = MLPClassifierManualSetup.MLPClassifierOverride(hidden_layer_sizes=self.layers, warm_start=True)
            self.net.set_coeffs(coefs, intercepts)
            self.net.fit(inputs, directions)
            self.net.coefs_ = coefs
            self.net.intercepts_ = intercepts

            print("Do coefs match? " + str(original_coefs == self.net.coefs_))

    def select_key_from_net(self):
        return self.net.predict([self.inputs])

    def select_shortest_pellet_route(self):
        print(self.inputs[5:9])
        min_index = self.inputs[5:9].index(min(self.inputs[5:9]))
        print(min_index)
        if min_index == 0:
            return "up"
        elif min_index == 1:
            return "down"
        elif min_index == 2:
            return "right"
        elif min_index == 3:
            return "left"

    def select_random_key(self):
        selection = random.randint(0, 3)

        return directions[selection]

    def end_game(self, score):
        self.final_score = score
        print("Final Score: %s" % score)
        self.game_ended = True

if __name__ == "__main__":
    Jarvis(0, 0, [5, 3]).start_game()