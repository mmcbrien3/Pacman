import Jarvis
import random, time
from multiprocessing import Process
from sklearn.externals import joblib

layers = [5]

class GeneticHandler(object):

    def __init__(self, popsize=50, elite_percent=0.05, keep_chance=0.1, mutate_chance = 0.05, numgenerations=None):
        self.elite = int(popsize*elite_percent)
        self.keep = int(popsize*keep_chance)
        self.mutate_chance = mutate_chance
        self.popsize = popsize
        self.cur_generation = {}
        self.threads = []
        self.numgenerations = numgenerations if not numgenerations is None else 9999
        self.start_life()

    def start_life(self):
        self.gens = 0
        for i in range(self.popsize):
            self.cur_generation[self.make_random_player(i)] = 0

        while self.gens < self.numgenerations:
            self.gens += 1
            self.run_generation()
            self.evolve()



    def make_random_player(self, id):
        return Jarvis.Jarvis(self.gens, id, layers)

    def run_generation(self):
        self.threads = []
        for j in self.cur_generation:
            j.start_game()
            self.cur_generation[j] = j.final_score


    def evolve(self):
        nets_by_score = sorted(self.cur_generation.items(), key=lambda kv: kv[1])
        print("Sorted nets")
        print(nets_by_score)
        total_fitness, segmented_fitness = self.get_total_fitness(nets_by_score)
        nets_by_score = [j[0] for j in nets_by_score]
        elites = nets_by_score[len(nets_by_score)-self.elite:]

        best = nets_by_score[-1]
        joblib.dump(best.net, r".\Best.sav")

        for e in elites:
            e.final_score = 0

        num_in_gen = 1

        new_generation = elites
        num_remaining = self.popsize - len(new_generation)

        for i in range(num_remaining):
            mother, father = self.select_parents(nets_by_score, total_fitness, segmented_fitness)
            new_generation.append(self.breed(mother, father, num_in_gen))
            num_in_gen += 1

        self.cur_generation = {}
        for player in new_generation:
            self.cur_generation[player] = 0

    def get_total_fitness(self, nets):
        total = 0
        segmented = []
        for k, v in nets:
            total += v
            segmented.append(total)
        return total, segmented

    def select_parents(self, nets, total_fitness, segmented_fitness):
        r = random.randint(0, total_fitness)
        for i in range(len(segmented_fitness)):
            if r <= segmented_fitness[i]:
                break
        mother = nets[i]
        r = random.randint(0, total_fitness)
        for i in range(len(segmented_fitness)):
            if r <= segmented_fitness[i]:
                break
        father = nets[i]
        return mother, father


    def breed(self, mother, father, id):

        mother_coefs = mother.net.coefs_
        father_coefs = father.net.coefs_
        child_coefs = father_coefs[:]
        for i in range(len(mother_coefs)):
            for j in range(len(mother_coefs[i])):
                for k in range(len(mother_coefs[i][j])):
                    if random.random() <= self.mutate_chance:
                        if random.randint(0, 1) == 1:
                            child_coefs[i][j][k] = mother_coefs[i][j][k]
                    else:
                        if random.randint(0, 1) == 1:
                            child_coefs[i][j][k] = mother_coefs[i][j][k] * (random.random()*3-1.5)
                        else:
                            child_coefs[i][j][k] = father_coefs[i][j][k] * (random.random()*3-1.5)
                        
        mother_intercepts = mother.net.intercepts_
        father_intercepts = father.net.intercepts_
        child_intercepts = father_intercepts[:]
        for i in range(len(mother_intercepts)):
            for j in range(len(mother_intercepts[i])):
                if random.random() <= self.mutate_chance:
                    if random.randint(0, 1) == 1:
                        child_intercepts[i][j] = mother_intercepts[i][j]
                else:
                    if random.randint(0, 1) == 1:
                        child_intercepts[i][j] = mother_intercepts[i][j] * (random.random()*3-1.5)
                    else:
                        child_intercepts[i][j] = father_intercepts[i][j] * (random.random()*3-1.5)

        return Jarvis.Jarvis(self.gens, id, layers, child_coefs, child_intercepts)



    def mutate(self, id, parent):
        parent_coefs = parent.net.coefs_
        child_coefs = parent_coefs[:]
        for i in range(len(parent_coefs)):
            for j in range(len(parent_coefs[i])):
                for k in range(len(parent_coefs[i][j])):
                    child_coefs[i][j][k] = parent_coefs[i][j][k] * (random.random() * 3 - 1.5)

        parent_intercepts = parent.net.intercepts_
        child_intercepts = parent_intercepts[:]
        for i in range(len(parent_intercepts)):
            for j in range(len(parent_intercepts[i])):
                child_intercepts[i][j] = parent_intercepts[i][j] * (random.random() * 3 - 1.5)

        return Jarvis.Jarvis(self.gens, id, layers, child_coefs, child_intercepts)

if __name__ == '__main__':
    GeneticHandler()
