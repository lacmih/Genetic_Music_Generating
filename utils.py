from midiutil import MIDIFile
from pyo import Metro, CosTable, TrigEnv, Iter, Sine
import os

def int_from_bits(bits):
    return int(sum([bit*pow(2, index) for index, bit in enumerate(bits)]))

def metronome(bpm: int):
    met = Metro(time=1 / (bpm / 60.0)).play()
    t = CosTable([(0, 0), (50, 1), (200, .3), (500, 0)])
    amp = TrigEnv(met, table=t, dur=.25, mul=1)
    freq = Iter(met, choice=[660, 440, 440, 440])
    return Sine(freq=freq, mul=amp).mix(2).out()

def save_genome_to_midi(melodies):
    for melody in melodies:
        if len(melody["notes"][0]) != len(melody["beat"]) or len(melody["notes"][0]) != len(melody["velocity"]):
            raise ValueError

    mf = MIDIFile(1)

    time = 0.0
    track = 0
    bpm = 120
    prog = [40, 0, 60, 69]
    mf.addTrackName(track, time, "Sample Track")
    mf.addTempo(track, time, bpm)

    for ind, melody in enumerate(melodies):
        channel = ind
        program = prog[ind] # Selecting instrument
        mf.addProgramChange(track, channel, time, program) # Changing instrument from a fiven time at a given auido channel
        
        for i, vel in enumerate(melody["velocity"]):
            if vel > 0:
                for step in melody["notes"]:
                    mf.addNote(track, channel, step[i], time, melody["beat"][i], vel)

            time += melody["beat"][i]

        time = 0.0

    filename = "./generated_music/music_3.mid"

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        mf.writeFile(f)