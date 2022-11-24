from pyo import Server, Events, EventScale, EventSeq
import time
import random
from utils import *
from fitness_functions import direction_fitness, stability_fitness, entropy_fitness
from genetic_functions import genetic_algorithm
# random.seed(1)

KEYS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F",
        "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
SCALES = ["major", "minorM", "dorian", "phrygian",
          "lydian", "mixolydian", "majorBlues", "minorBlues"]
BITS_PER_NOTE = 4
# INSTRUMENTS = ["prophet", "dsaw", "fm", "tb303", "pulse", "piano", "blade", "beep"]

s = Server()
s.setOutputDevice(16)
s.boot()

scl = EventScale(root='C', scale='major', first=4)
n_notes = 24
num_notes = 4

def listen_to_the_music(events):
    m = metronome(128)

    for e in events:
        print(e)
        e.play()
    s.start()

    time.sleep(10)

    for e in events:
        e.stop()
    s.stop()

def generate_notes(n_notes):
    notes = [[round(random.random()) for _ in range(4)]
             for _ in range(n_notes)]
    return notes 

def notes_to_chords(melody, notes, beats, scl):
    notes_ind = [int_from_bits(note)for note in notes]

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


def generate_music(scl, n_notes, fitness, n_iter, n_pop, r_cross, r_mut, n_instruments):

    melodies = [{ "notes": [], "velocity": [], "beat": [] } for i in range(n_instruments)]

    for i in range(n_instruments):
        best_notes, score, best_beats = genetic_algorithm(fitness, n_iter, n_pop, r_cross, r_mut)

        melodies[i] = notes_to_chords(melodies[i], best_notes, best_beats, scl)

    save_genome_to_midi(melodies)

    # return [
    #     Events(
    #         midinote=EventSeq(step, occurrences=1),
    #         midivel=EventSeq(melody["velocity"], occurrences=1),
    #         beat=EventSeq(melody["beat"], occurrences=1),
    #         # attack=0.001,
    #         # decay=0.05,
    #         # sustain=0.5,
    #         # release=0.005,
    #         # bpm = 128
    #     ) for step in melody["notes"]
    # ]


# direction_fitness, stability_fitness, entropy_fitness
fitness = [direction_fitness, stability_fitness, entropy_fitness]
n_iter = 100
n_pop = 100
r_cross = 0.2
r_mut = 0.05
n_instruments = 2
# events = generate_music(scl, n_notes, fitness, n_iter, n_pop, r_cross, r_mut, n_instruments)
generate_music(scl, n_notes, fitness, n_iter, n_pop, r_cross, r_mut, n_instruments)
# listen_to_the_music(events)

# Általánosítani kellene: Hogy melyik hang melyik időben érkezik (adott hangszeren ha egyszerre több hangot (pl akkordot)
# akarunk játszani; time tömb. Utilsba használni. Általánosítani a módszert n hangszerre, a fitness 
# függvények tudják ezt kezelni). -> Tehát általánosítani a genetikus algoritmust a fitness függvényekkel együtt 
# több hangszerre
# Behúzni egy hálót, mint fitness függvényt, amelyik a stílusra vonatkozik

