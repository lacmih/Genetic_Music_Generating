from numpy.random import randint
from numpy.random import rand
from fitness_functions import direction_fitness, stability_fitness, entropy_fitness, chords_fitness, beat_fitness

from utils import int_from_bits
from numpy import random

import numpy as np

# random.seed(1)

def random_gene():
    s = [round(rand()) for _ in range(4)]
    return s

def random_element(k=100):
    return [random_gene() for _ in range(k)]

def random_chord(k=100):
    ch = [0]
    for i in range(round(k/3)):
        random = round(rand() * 12)
        ch.append(random)
        ch.append(random + 2)
        ch.append(random + 4)
    return ch    

def random_velocity(k=100):
    return [random.choice([127, 63, 31]) for _ in range(k)]

def same_beat(k=100):
    return [random.choice([1]) for _ in range(k)]

def random_beat(k=100):
    return [random.choice([2, 1, 1/2]) for _ in range(k)]

def random_single_beat():
    return random.choice([2, 1, 1/2])

def random_time(k=100):
    return [random.choice([0, 1]) for _ in range(k)]

def mutation(elem, c):
    # iterate over the population and mutate with a chance of c
    mute = rand()
    if mute > c:
        e = random_gene()
        pos = randint(0, len(elem) - 1)
        elem[pos] = e
    return elem

def mutation_beat(elem, c):
    # iterate over the population and mutate with a chance of c
    mute = rand()
    if mute > c:
        e = random_single_beat()
        pos = randint(0, len(elem) - 1)
        elem[pos] = e
    return elem

def mutation_chord(elem, c):
    # iterate over the population and mutate with a chance of c
    mute = rand()
    if mute > c:
        e = round(rand() * 16)
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
    pop = [random_element() for _ in range(n_pop)]

    pop_int = [[int_from_bits(note) for note in pop_elem] for pop_elem in pop]

    best, best_eval = 0.0, 0.0
    for gen in range(n_iter):
        print("Generation number: " + str(gen), end='\r')

        scores = [np.array([fit_func(c) for c in pop_int]) for fit_func in fitness]
        sc = np.zeros(len(pop_int))

        for i in scores:
            sc += i
        scores = sc

        for i in range(n_pop):
            if scores[i] > best_eval:
                best, best_eval = pop[i], scores[i]

        selected = [selection(pop, scores) for _ in range(n_pop)]
        children = list()
        for i in range(0, n_pop, 2):
            p1, p2 = selected[i], selected[i+1]
            for c in crossover(p1, p2, r_cross):
                mutation(c, r_mut)
                children.append(c)
        
        pop = children
        pop_int = [[int_from_bits(note) for note in pop_elem] for pop_elem in pop]
    
    # Generating the beats 
    beat_pop = [random_beat() for _ in range(n_pop)]
    fitness = [beat_fitness]
    for gen in range(n_iter):
        # print(beat_pop)
        print("Generation number: " + str(gen), end='\r')
        scores = [np.array([fit_func(c) for c in beat_pop]) for fit_func in fitness]
        sc = np.zeros(len(beat_pop))

        # print(scores)

        for i in scores:
            sc += i
        scores = sc

        for i in range(n_pop):
            if scores[i] > best_eval:
                best, best_eval = pop[i], scores[i]

        selected = [selection(beat_pop, scores) for _ in range(n_pop)]
        children = list()
        for i in range(0, n_pop, 2):
            p1, p2 = selected[i], selected[i+1]
            for c in crossover(p1, p2, r_cross):
                mutation_beat(c, r_mut)
                children.append(c)
        
        beat_pop = children

    
    return [best, best_eval, random_beat()]


def genetic_algorithm_accorded(fitness, n_iter, n_pop, r_cross, r_mut):

    fitness.append(chords_fitness)
    pop = [random_element() for _ in range(n_pop)]
    pop_int = [[int_from_bits(note) for note in pop_elem] for pop_elem in pop]
    best, best_eval = 0.0, 0.0

    for gen in range(n_iter):
        print("Generation number: " + str(gen), end='\r')
        scores = [np.array([fit_func(c) for c in pop_int]) for fit_func in fitness]
        sc = np.zeros(len(pop_int))

        for i in scores:
            sc += i
        scores = sc

        for i in range(n_pop):
            if scores[i] > best_eval:
                best, best_eval = pop[i], scores[i]

        selected = [selection(pop, scores) for _ in range(n_pop)]
        children = list()
        for i in range(0, n_pop, 2):
            p1, p2 = selected[i], selected[i+1]
            for c in crossover(p1, p2, r_cross):
                mutation(c, r_mut)
                children.append(c)

        pop = children
        pop_int = [[int_from_bits(note) for note in pop_elem] for pop_elem in pop]
    return [best, best_eval, same_beat()]

def genetic_algorithm_accorded_fully(fitness, n_iter, n_pop, r_cross, r_mut):
    fitness.append(chords_fitness)
    k = 199

    pop_int = [random_chord(k) for _ in range(n_pop)]
    pop = pop_int.copy()
    best, best_eval = 0.0, 0.0
    for gen in range(1):
        print("Generation number: " + str(gen), end='\r')
        scores = [np.array([fit_func(c) for c in pop_int]) for fit_func in fitness]
        sc = np.zeros(len(pop_int))
        for i in scores:
            sc += i
        scores = sc

        for i in range(n_pop):
            if scores[i] > best_eval:
                best, best_eval = pop[i], scores[i]

        selected = [selection(pop, scores) for _ in range(n_pop)]
        children = list()
        for i in range(0, n_pop, 2):
            p1, p2 = selected[i], selected[i+1]
            for c in crossover(p1, p2, r_cross):
                mutation_chord(c, r_mut)
                children.append(c)

        pop = children
        pop_int = [random_chord(k) for _ in range(n_pop)]
    return [best, best_eval, same_beat(k)]

def genetic_algorithm_rithmic(fitness, n_iter, n_pop, r_cross, r_mut):
    k = 100
    notes = [0 for _ in range(k)]
    beat = [1.0 for _ in range(k)]
    scores = [fit_func(notes) for fit_func in fitness]
    return [notes, scores, beat]



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