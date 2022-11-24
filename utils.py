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

def save_genome_to_midi(melody, melody2):
    if len(melody["notes"][0]) != len(melody["beat"]) or len(melody["notes"][0]) != len(melody["velocity"]):
        raise ValueError

    mf = MIDIFile(1)

    track   = 0
    channel = 0
    time    = 0 # Eight beats into the composition
    program = 40 # Selecting instrument
    mf.addProgramChange(track, channel, time, program) # Changing instrument from a fiven time at a given auido channel

    track = 0
    channel = 0
    bpm = 120

    time = 0.0
    mf.addTrackName(track, time, "Sample Track")
    mf.addTempo(track, time, bpm)

    for i, vel in enumerate(melody["velocity"]):
        if vel > 0:
            for step in melody["notes"]:
                mf.addNote(track, channel, step[i], time, melody["beat"][i], vel)

        time += melody["beat"][i]
    
    track   = 0
    channel = 1
    time    = 0 # Eight beats into the composition
    program = 1 # Selecting instrument
    mf.addProgramChange(track, channel, time, program) # Changing instrument from a fiven time at a given auido channel

    channel = 1
    bpm = 120
    for i, vel in enumerate(melody2["velocity"]):
        if vel > 0:
            for step in melody2["notes"]:
                mf.addNote(track, channel, step[i], time, melody2["beat"][i], vel)

        time += melody2["beat"][i]

    filename = "./generated_music/music_3.mid"

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        mf.writeFile(f)