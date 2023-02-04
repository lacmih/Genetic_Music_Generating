from pyo import Server, Events, EventScale, EventSeq
import time
import random
from utils import triplewise, save_genome_to_midi, int_from_bits
from fitness_functions import direction_fitness, stability_fitness, entropy_fitness, style_fitness
from genetic_functions import genetic_algorithm, genetic_algorithm_accorded, genetic_algorithm_accorded_fully, genetic_algorithm_rithmic

# KEYS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F",
#         "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]

KEYS = ["C", "D", "E", "F", "G", "A", "B"]
# SCALES = ["major", "minorM", "dorian", "phrygian",
#           "lydian", "mixolydian", "majorBlues", "minorBlues"]
# BITS_PER_NOTE = 4

s = Server()
s.setOutputDevice(16)
s.boot()

scl = EventScale(root='Eb', scale='major', first=4)
scales = [EventScale(root=key, scale='major', first=4) for key in KEYS]
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

# i -> the index of instrument the first will be rewarded on accords
def notes_to_chords(melody, notes, beats, scl, instrument_ind):

    ## if genetic_algorithm_accorded_fully is used, we get integers, not binary data
    notes_ind = []
    if instrument_ind == 0 or instrument_ind == 1:
        notes_ind = notes
    else:
        notes_ind = [int_from_bits(note)for note in notes]

    # print(notes_ind)

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

    
    # filling up the time array, making the chords play at the same time
    if instrument_ind == 0:
        # print(melody["beat"])
        # print(len(melody["beat"]))
        k = 0 # if chord, dont check it for the rest of chord
        for p,i in enumerate(triplewise(melody["notes"])):
            if k == 0: 
                if (i[0] != 14) and (i[2] != 14) and \
                ((i[0] - i[1] == 2 and i[1] - i[2] == 2) or \
                (i[2] - i[1] == 2 and i[1] - i[0] == 2)):

                    melody["beat"][p] = melody["beat"][p] * 3
                    melody["beat"][p + 1] = melody["beat"][p + 1] * 3
                    melody["beat"][p + 2] = melody["beat"][p + 2] * 3

                    [melody["time"].append(0.0) for _ in range(2)]
                    melody["time"].append(3.0)


                    # print("AKKORD")
                    k = 2 # the rest of the chord is not checked
                else:
                    melody["time"].append(melody["beat"][p])
            else:
                k -= 1
        # The remain notes, if the last three is not a chord
        if k != 2:
            l = len(melody["beat"])
            melody["time"].append(melody["beat"][l - 2])
            melody["time"].append(melody["beat"][l - 1])
        # melody["beat"] = [beat * 3 for beat in melody["beat"]]
        # melody["beat"][0] = 1.0
        # melody["beat"][1] = 2.0
        # melody["beat"][2] = 3.0
        # melody["beat"][3] = 1.0
        # print(melody["beat"])
        # print(len(melody["beat"]))
        # print(len(melody["notes"]))

    else:
        melody["time"] = melody["beat"]

    # print(melody["time"])
    # print(len(melody["time"]))

    steps = []
    # print(scl)
    # for i in range(len(scl)):
    #     print(scl[i])

    for step in range(1):
        steps.append([scl[note % len(scl)] for note in melody["notes"]])

    melody["notes"] = steps

    return melody


def generate_music(scl, n_notes, fitness, n_iter, n_pop, r_cross, r_mut, n_instruments):
    melodies = [{ "notes": [], "velocity": [], "beat": [], "time": [] } for i in range(n_instruments)]

    for i in range(n_instruments):
        match i:
            case 0:
                best_notes, score, best_beats = genetic_algorithm_accorded_fully(fitness, n_iter, n_pop, r_cross, r_mut)
                melodies[i] = notes_to_chords(melodies[i], best_notes, best_beats, scl, i)
            case 1:
                best_notes, score, best_beats = genetic_algorithm_rithmic(fitness, n_iter, n_pop, r_cross, r_mut)
                melodies[i] = notes_to_chords(melodies[i], best_notes, best_beats, scl, i)
            case _:
                best_notes, score, best_beats = genetic_algorithm(fitness, n_iter, n_pop, r_cross, r_mut)
                melodies[i] = notes_to_chords(melodies[i], best_notes, best_beats, scl, i)

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
r_cross = 0.7
r_mut = 0.05
n_instruments = 3
# events = generate_music(scl, n_notes, fitness, n_iter, n_pop, r_cross, r_mut, n_instruments)
generate_music(scl, n_notes, fitness, n_iter, n_pop, r_cross, r_mut, n_instruments)
# listen_to_the_music(events)

# Váltani az adott skálák között, Berakni egy dobot, ahhoz igazítani a tempót
# Több osztályra osztani a hangszereket (mint ahogy rendesen): tempó, akkord, dallam
# Kitalálni a tempóra fitnesst