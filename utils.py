import os
import numpy as np

from midiutil import MIDIFile
from pyo import Metro, CosTable, TrigEnv, Iter, Sine
import librosa

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

    filename = "./generated_music/music_act.mid"

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        mf.writeFile(f)

def get_features(y, sr):
    
    chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
    rmse = librosa.feature.rms(y=y)
    spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    zcr = librosa.feature.zero_crossing_rate(y)
    harmony, perceptr = librosa.effects.hpss(y) 
    tempo = librosa.beat.tempo(y=y, sr=sr)
    
    mfccs = librosa.feature.mfcc(y=y, sr=sr)
    mfccs_means = np.mean(mfccs.T, axis=0),
    mfccs_var = np.var(mfccs.T, axis=0)
   
    res = [np.mean(chroma_stft), np.var(chroma_stft), np.mean(rmse), np.var(rmse), np.mean(spec_cent), np.var(spec_cent), np.mean(spec_bw), np.var(spec_bw), np.mean(rolloff), np.var(rolloff), np.mean(zcr), np.var(zcr), np.mean(harmony), np.var(harmony), np.mean(perceptr), np.var(perceptr), tempo[0]]
    
    for i in range(0, 20):
        res.append(mfccs_means[0][i])
        res.append(mfccs_var[i])
    
    return res

def predict(f, model):
    y, s = librosa.load(f)
    y, _ = librosa.effects.trim(y)
    f = get_features(y, s)

    f = np.array(f)
    f = f.reshape(1, -1)

    probs =  model.predict_proba(np.array(f))
    classes = model.classes_

    print(classes)
    print(probs[0])
    print(classes[np.argmax(probs[0])])
    print(np.max(probs[0]))

    return classes[np.argmax(probs[0])], np.max(probs[0]), probs[0]