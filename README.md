Here’s a **complete, polished `README.md`** tailored to the MIDI project you’ve been building (API, clock, file, chord, pattern, ports, device).  
You can copy-paste this directly.

---

# 🎹 MaxMIDI

**MaxMIDI** is a lightweight, pure-Python MIDI library that combines **low-level MIDI access** with **musical abstractions** like chords, patterns, clocks, and MIDI file support.

It is designed to be:
- 🧩 Modular
- 🎼 Musical
- 🛠 Backend-agnostic (WinMM / ALSA / CoreMIDI)
- 📦 Easy to embed in creative coding, DAWs, and tools

---

## ✨ Features

### Core MIDI
- MIDI input & output ports
- Device discovery
- Safe message construction
- SysEx support

### Musical Abstractions
- Chords (`C`, `Am7`, `G7`, `F#dim`)
- Arpeggiators
- Note & drum patterns
- Scales (optional extension)

### Timing & Sync
- MIDI clock (24 PPQN)
- Start / Stop / Continue
- BPM control

### MIDI Files
- Read & write Standard MIDI Files (SMF)
- Type 0 and Type 1
- Tempo, time signature, key signature
- Note events

---

## 📦 Installation

Clone the repository and install locally:

```bash
git clone https://github.com/yourname/maxmidi.git
cd maxmidi
pip install -e .
```

---

## 🚀 Quick Start

### Play a note

```python
from maxmidi import Midi

with Midi() as m:
    m.note_on(60, 100)
    m.sleep(0.5)
    m.note_off(60)
```

---

### Play a chord

```python
from maxmidi import Midi, Chord

with Midi() as m:
    Chord("Am7").play(m, duration=1.0)
```

---

### Arpeggiate a chord

```python
from maxmidi import Midi, Chord, Arpeggiator

with Midi() as m:
    chord = Chord("Cmaj7")
    arp = Arpeggiator(chord.notes(), step_time=0.15)
    arp.play(m)
```

---

## ⏱ MIDI Clock

```python
from maxmidi import Midi, MidiClock
import time

with Midi() as m:
    clock = MidiClock(m, bpm=120)
    clock.start()
    time.sleep(4)
    clock.stop()
```

---

## 🥁 Patterns

### Note Pattern

```python
from maxmidi import Midi, NotePattern

pattern = NotePattern(
    steps=[60, None, 62, None, 64, None, 67, None],
    step_time=0.25
)

with Midi() as m:
    pattern.play(m)
```

### Drum Pattern

```python
from maxmidi import Midi, DrumPattern

KICK = 36
SNARE = 38
HAT = 42

beat = DrumPattern(
    steps=[
        [KICK, HAT],
        HAT,
        [SNARE, HAT],
        HAT,
    ],
    step_time=0.25
)

with Midi() as m:
    beat.play(m)
```

---

## 💾 MIDI Files

### Write a MIDI file

```python
from maxmidi import MidiFile

mf = MidiFile()
track = mf.add_track()

track.tempo(0, 120)
track.note_on(0, 60, 100)
track.note_off(480, 60)

mf.save("example.mid")
```

### Read a MIDI file

```python
mf = MidiFile.load("example.mid")

for track in mf.tracks:
    for event in track.events:
        print(event)
```

---

## 🎛 Ports & Devices

```python
from maxmidi import list_outputs, open_output

print(list_outputs())

midi = open_output(0)
midi.send(0x90, 60, 100)
```

---

## 📁 Project Structure

```text
src/maxmidi/
  api.py        # High-level MIDI API
  message.py    # MIDI message helpers
  ports.py      # Port discovery
  device.py     # Device abstraction
  clock.py      # MIDI clock & transport
  file.py       # MIDI file I/O
  chord.py      # Chords & harmony
  pattern.py    # Patterns & arpeggiators
```

---

## 🎯 Design Philosophy

- **Low-level where needed**, musical where it matters
- No external dependencies
- Explicit timing (no magic schedulers)
- Easy to extend for generative music

---

## 🛣 Roadmap

- MIDI input callbacks
- Quantized / clock-synced patterns
- Scale & progression engine
- Async / real-time scheduler
- Plugin-style backend system

---

## 📜 License

MIT License

---

## 🙌 Inspiration

Inspired by:
- MIDI 1.0 Specification
- MIDIUtil
- RtMidi
- Creative coding workflows

---

If you want, I can:
- Add **usage badges**
- Write **API docs**
- Create a **CLI**
- Add **examples/** folder

Just tell me what you want next. 🎹
