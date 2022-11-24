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

melody = {
    "notes": [],
    "velocity": [],
    "beat": []
}
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

def notes_to_chords(melody, notes, scl):
    notes_ind = [int_from_bits(note)for note in notes]

    note_length = 4 / num_notes
    a = 0
    for note in notes_ind:

       
        if note > 14:
            melody["notes"] += [0]
            melody["velocity"] += [0]
            melody["beat"] += [note_length]

        else:
            # Demonstration: You can make the note shorter (beat dec), or make it quieter (velocity dec)
            if a == 0:
                melody["velocity"] += [127]
                a = 1
                melody["beat"] += [note_length]
            else:
                melody["velocity"] += [60]
                a = 0
                melody["beat"] += [note_length/2]

            melody["notes"] += [note]
            # melody["velocity"] += [127]
            # melody["beat"] += [note_length]
        

    steps = []
    for step in range(1):
        steps.append([scl[note % len(scl)] for note in melody["notes"]])

    melody["notes"] = steps

    save_genome_to_midi(melody)
    return melody


def generate_music(melody, scl, n_notes, fitness, n_iter, n_pop, r_cross, r_mut):

    best_notes, score = genetic_algorithm(fitness, n_iter, n_pop, r_cross, r_mut)

    notes_to_chords(melody, best_notes, scl)

    return [
        Events(
            midinote=EventSeq(step, occurrences=1),
            midivel=EventSeq(melody["velocity"], occurrences=1),
            beat=EventSeq(melody["beat"], occurrences=1),
            # attack=0.001,
            # decay=0.05,
            # sustain=0.5,
            # release=0.005,
            # bpm = 128
        ) for step in melody["notes"]
    ]


# direction_fitness, stability_fitness, entropy_fitness
fitness = [direction_fitness, stability_fitness, entropy_fitness]
n_iter = 100
n_pop = 100
r_cross = 0.2
r_mut = 0.05
events = generate_music(melody, scl, n_notes, fitness, n_iter, n_pop, r_cross, r_mut)

# listen_to_the_music(events)
