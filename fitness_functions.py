from scipy.stats import entropy
from utils import predict, save_genome_to_midi
from midi2audio import FluidSynth
from joblib import load
# from genetic_music_generator import notes_to_chords
# from genetic_functions import random_beat
from pyo import EventScale
from numpy import random
from utils import int_from_bits, triplewise


labels = ['blues', 'classical', 'country', 'disco', 'hiphop', 'jazz', 'metal', 'pop', 'reggae', 'rock']
model = load('./genre-classifier/xgb.joblib')

# Defining different functions, that add up the fitness value

# Subraters from paper Apply evolutionary algorithms for music generation
# url: https://odr.chalmers.se/server/api/core/bitstreams/2a2d8e3b-d16f-4d4d-8edd-ecdd599f1bfd/content

def notes_to_chords(melody, notes, beats, scl):
    notes_ind = notes
    num_notes = 4

    note_length = 4 / num_notes
    a = 0
    for e, note in enumerate(notes_ind):
       
        if note > 14:
            melody["notes"] += [0]
            melody["velocity"] += [0]
            melody["beat"] += [note_length]

        else:
            # You can make the note shorter (beat dec), or make it quieter (velocity dec)
            melody["beat"] += [note_length * beats[e]] # the beats array element scales the normal beat length
            melody["notes"] += [note]
            melody["velocity"] += [127]

    steps = []
    for step in range(1):
        steps.append([scl[note % len(scl)] for note in melody["notes"]])

    melody["notes"] = steps

    return melody

def random_beat(k=100):
    return [random.choice([1]) for _ in range(k)]


# Direction of melody:
def direction_fitness(melody_notes): #novekedjen
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
def stability_fitness(melody_notes): # novelni
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
    return (n_change_dir / len(melody_notes))

def entropy_fitness(melody_notes):
    
    # Notes into a Probability Distribution Function
    probs = [0 for i in range(16)] #! hardcoded 16-> number of possible note types
    
    for i in melody_notes:
        probs[i - 1] += 1
    
    l = len(melody_notes)
    probs = [p/l for p in probs]

    return (entropy(probs, base = len(probs)))

# Adott hangszerre megnézi, hogy az egymást követően leadott 3-hangok hány százaléka akkord
def chords_fitness(melody_notes):
    acc = 0
    for i in triplewise(melody_notes):
        if (i[0] != 14) and (i[2] != 14) and \
            ((i[0] - i[1] == 2 and i[1] - i[2] == 2) or \
            (i[2] - i[1] == 2 and i[1] - i[0] == 2)):
            acc += 1
    # print(acc/(len(melody_notes)/3))
    return (acc/(len(melody_notes)/3))


def beat_fitness(melody_beats):
    ind = 0
    sum_beats = 0
    dist = 0
    average_beat = 4
    for i in melody_beats:
        if ind < 4:
            sum_beats += i
        else:
            dist += abs(sum_beats - average_beat)
            sum_beats = 0
            ind = -1
        ind += 1
    return dist
    
# Adott zenének visszaadja, hány százalékban adott stílusú
def style_fitness(melodies):
    global labels, model
    style = 'classical'

    # print(melodies)

    melody = { "notes": [], "velocity": [], "beat": [] }
    scl = EventScale(root='C', scale='major', first=4)
    melody = notes_to_chords(melody, melodies, random_beat(), scl)
    save_genome_to_midi([melody])

    FluidSynth().midi_to_audio('./generated_music/music_act.mid', './generated_music/music_act.wav')
    
    ii = 0
    for p, i in enumerate(labels):
        if style == i:
            ii = p
            break

    label, proc, probs = predict('./generated_music/music_act.wav', model)
    return probs[ii]


