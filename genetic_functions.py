from numpy.random import randint
from numpy.random import rand
from fitness_functions import direction_fitness, stability_fitness, entropy_fitness

from utils import int_from_bits
from numpy import random

import numpy as np

# random.seed(1)

def random_gene():
    s = [round(rand()) for _ in range(4)]
    return s


def random_element(k=100):
    return [random_gene() for _ in range(k)]

def random_velocity(k=100):
    return [random.choice([127, 63, 31]) for _ in range(k)]

def random_beat(k=100):
    return [random.choice([1]) for _ in range(k)]


def mutation(elem, c):
    # iterate over the population and mutate with a chance of c
    mute = rand()
    if mute > c:
        e = random_gene()
        pos = randint(0, len(elem) - 1)
        elem[pos] = e
    return elem


def crossover(parent1, parent2, r_cross):

    if len(parent1) != len(parent2):
        raise ValueError("Parents must be of the same length")
    child1, child2 = parent1.copy(), parent2.copy()

    if rand() > r_cross:
        # select crossover point that is not on the end of the string
        cross_point = randint(0, len(parent1) - 1)
        child1 = parent1[:cross_point] + parent2[cross_point:]
        child2 = parent2[:cross_point] + parent1[cross_point:]

    return child1, child2


# tournament selection
def selection(pop, scores, k=3):
    # first random selection
    selection_ix = randint(len(pop))
    for ix in randint(0, len(pop), k-1):
        # check if better (e.g. perform a tournament)
        if scores[ix] < scores[selection_ix]:
            selection_ix = ix
    return pop[selection_ix]


def genetic_algorithm(fitness, n_iter, n_pop, r_cross, r_mut):
    # initial population of random bitstring
    pop = [random_element() for _ in range(n_pop)]

    pop_int = [[int_from_bits(note) for note in pop_elem] for pop_elem in pop]# For the fitness calculation, we need the exact numbers

    # keep track of best solution
    best, best_eval = 0.0, 0.0
    # enumerate generations
    for gen in range(n_iter):
        # if gen % 100 == 0:
        print("Generation number: " + str(gen), end='\r')
        # evaluate all candidates in the population

        scores = [np.array([fit_func(c) for c in pop_int]) for fit_func in fitness]
        sc = np.zeros(len(pop_int))

        for i in scores:
            sc += i
        
        scores = sc

        # check for new best solution
        for i in range(n_pop):
            if scores[i] > best_eval:
                best, best_eval = pop[i], scores[i]
                # print(">%d, new best f(%s) = %.3f" % (gen,  pop[i], scores[i]))
        # select parents
        selected = [selection(pop, scores) for _ in range(n_pop)]
        # create the next generation
        children = list()
        for i in range(0, n_pop, 2):
            # get selected parents in pairs
            p1, p2 = selected[i], selected[i+1]
            # crossover and mutation
            for c in crossover(p1, p2, r_cross):
                # mutation
                mutation(c, r_mut)
                # store for next generation
                children.append(c)
        # replace population
        pop = children
        pop_int = [[int_from_bits(note) for note in pop_elem] for pop_elem in pop]
    return [best, best_eval, random_beat()]


def fitness(elem):
    f = 0
    for note in elem:
        s = sum(note)
        f += s
    return f

def main():
    best, score = genetic_algorithm([entropy_fitness], 2, 100, 0.2, 0.05)
    print('Done!')
    print('f(%s) = %f' % (best, score))

if __name__ == "__main__":
    main()