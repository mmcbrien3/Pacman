"""
2-input XOR example -- this is most likely the simplest possible example.
"""

from __future__ import print_function
import os
import neat, GameController
# 2-input XOR inputs and expected outputs.
pac_inputs = [(0, 0,  0, 0, 1, 1, 1, 0, 0, -1), (0, 0,  0, 0, 1, 1, 0, 1, 0, 1), (0, 0,  0, 0, 0, 1, 1, 1, -1, 0), (0, 0,  0, 0, 1, 0, 1, 1, 1, 0)]
pac_outputs = ["left", "right", "up", "down"]

class NEATHandler(object):

    def __init__(self, config_file, gens):
        self.gens = gens
        self.gen = 1
        self.num = 1
        self.numPerGen = 50

        self.run(config_file)


    def eval_genomes(self, genomes, config):
        for genome_id, genome in genomes:
            self.game_over = False
            self.final_score = 0
            self.inputs = []
            self.net = neat.nn.FeedForwardNetwork.create(genome, config)
            game = GameController.GameController(self)

            while not self.game_over:
                pass
            genome.fitness = self.final_score

            if self.num % self.numPerGen == 0:
                self.num = 1
                self.gen += 1
            self.num += 1

    def select_key_from_net(self):
        outputs = self.net.activate(self.inputs)
        return pac_outputs[outputs.index(max(outputs))]

    def end_game(self, score):
        self.game_over = True
        self.final_score = score

    def set_inputs(self, inputs):
        self.inputs = inputs

    def run(self, config_file):
        # Load configuration.
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_file)

        # Create the population, which is the top-level object for a NEAT run.
        p = neat.Population(config)

        # Add a stdout reporter to show progress in the terminal.
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        p.add_reporter(neat.Checkpointer(5))

        # Run for up to 300 generations.
        winner = p.run(self.eval_genomes, self.gens)

        # Display the winning genome.
        print('\nBest genome:\n{!s}'.format(winner))

        # Show output of the most fit genome against training data.
        print('\nOutput:')
        winner_net = neat.nn.FeedForwardNetwork.create(winner, config)


        p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
        p.run(self.eval_genomes, 10)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    NEATHandler(config_path, 300)