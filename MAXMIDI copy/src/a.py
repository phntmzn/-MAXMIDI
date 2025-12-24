# mymidi.py
from midiutil import MIDIFile

def create_simple_midi(filename="output.mid"):
    midi = MIDIFile(1)
    track = 0
    time = 0
    midi.addTrackName(track, time, "Sample Track")
    midi.addTempo(track, time, 120)

    midi.addNote(track, channel=0, pitch=60, time=0, duration=1, volume=100)
    midi.addNote(track, channel=0, pitch=64, time=1, duration=1, volume=100)
    midi.addNote(track, channel=0, pitch=67, time=2, duration=1, volume=100)

    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)
    print(f"MIDI saved as {filename}")