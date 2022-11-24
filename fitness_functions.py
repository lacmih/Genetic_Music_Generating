from scipy.stats import entropy

# Defining different functions, that add up the fitness value

# Subraters from paper Apply evolutionary algorithms for music generation
# url: https://odr.chalmers.se/server/api/core/bitstreams/2a2d8e3b-d16f-4d4d-8edd-ecdd599f1bfd/content

# Direction of melody:
def direction_fitness(melody_notes):
    # dir = 1 -> up -1 -> down

    prev = melody_notes[0]
    dir = 1
    n_act = 0
    n_same_dir = 0

    for i in melody_notes[1:len(melody_notes)]:
        if dir == 1:
            if i >= prev:
                n_act += 1
                if (n_act >= 3):
                    n_same_dir += 1
            else:
                dir = -1
                n_act = 1
        else:
            if i <= prev:
                n_act += 1
                if (n_act >= 3):
                    n_same_dir += 1
            else:
                dir = 1
                n_act = 1
        prev = i
    return n_same_dir / len(melody_notes)

# Stability of melody:
def stability_fitness(melody_notes):
    prev = melody_notes[0]

    dir = 1
    n_act = 0
    n_change_dir = 0

    if melody_notes[1] > melody_notes[0]:
        n_change_dir += 1

    for i in melody_notes[1:len(melody_notes)]:
        if dir == 1:
            if i < prev:
                n_change_dir += 1
                dir = -1
        else:
            if i > prev:
                n_change_dir += 1
                dir = 1
        prev = i
    return 1 - (n_change_dir / len(melody_notes))


def entropy_fitness(melody_notes):
    
    # Notes into a Probability Distribution Function
    probs = [0 for i in range(16)] #! hardcoded 16-> number of possible note types
    
    for i in melody_notes:
        probs[i - 1] += 1
    
    l = len(melody_notes)
    probs = [p/l for p in probs]

    return(entropy(probs, base = len(probs)))

# Adott hangszerre megnézi, hogy az egyidőben leadott hangok hány százaléka akkord
def chords_fitness(melodies):
    pass


