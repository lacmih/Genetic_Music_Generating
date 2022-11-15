from pyo import *
import time
import random
from utils import *
from fitness_functions import *
random.seed(1)

KEYS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
SCALES = ["major", "minorM", "dorian", "phrygian", "lydian", "mixolydian", "majorBlues", "minorBlues"]
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

def generate_notes(melody, scl, n_notes):
    notes = [[round(random.random()) for _ in range(4)] for _ in range(n_notes)]
    print(notes)

    notes_ind = [int_from_bits(note)for note in notes]

    print(notes_ind)


    note_length = 4 / num_notes

    for note in notes_ind:
        if note > 14:
            melody["notes"] += [0]
            melody["velocity"] += [0]
            melody["beat"] += [note_length]
        
        else:
            melody["notes"] += [note]
            melody["velocity"] += [127]
            melody["beat"] += [note_length]

    steps = []
    for step in range(1):
        steps.append([scl[note % len(scl)] for note in melody["notes"]])

    melody["notes"] = steps

    save_genome_to_midi(melody)

    return melody

def generate_music(melody, scl, n_notes):
    melody = generate_notes(melody, scl, n_notes)

    # melody["notes"] = [scl[note] for note in melody["notes"]]

    print(melody)

    print(direction_fitness(melody))

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


events = generate_music(melody, scl, n_notes)

# m = metronome(128)

# for e in events:
#     print(e)
#     e.play()
#     # time.sleep(1)
#     # e.stop()
# s.start()

# # time.sleep(5)

# for e in events:
#     e.stop()
# s.stop()
