# src/presets.py

from .chord import Chord
from .arpeggiator import Arpeggiator
from .drums import DrumPattern
from .sequencer import Sequencer
from .scale import Scale  # We'll assume you have or will add scale.py soon
from typing import List

class Presets:
    """
    Collection of ready-to-use musical presets.
    Use like: Presets.progressions.i_vi_iv_v("C").play()
    """

    class progressions:
        """Famous and useful chord progressions"""

        @staticmethod
        def i_v_vi_iv(key: str = "C", type: str = "maj7") -> Sequencer:
            """The ubiquitous pop progression: I–V–vi–IV (e.g., Journey - Don't Stop Believin')"""
            chords = [f"{key}", f"{key}5", f"{key}m", f"{key}IV"]
            return Sequencer.progression(chords, bpm=100)

        @staticmethod
        def ii_v_i(key: str = "C", type: str = "maj7") -> Sequencer:
            """Classic jazz turnaround"""
            roman = ["ii", "V", "I"]
            return Sequencer().progression(roman, key=key, bpm=140)

        @staticmethod
        def vi_iv_i_v(key: str = "Am") -> Sequencer:
            """Emotional minor progression (e.g., Adele style)"""
            return Sequencer.progression(["vi", "IV", "I", "V"], key=key, bpm=80)

        @staticmethod
        def andalusian(key: str = "Am") -> Sequencer:
            """Andalusian cadence: i–VII–VI–V"""
            return Sequencer.progression(["i", "VII", "VI", "V"], key=key, bpm=110)

        @staticmethod
        def pachelbel(key: str = "C") -> Sequencer:
            """Pachelbel's Canon: I–V–vi–iii–IV–I–IV–V"""
            chords = ["I", "V", "vi", "iii", "IV", "I", "IV", "V"]
            return Sequencer.progression(chords, key=key, bpm=90)

        @staticmethod
        def blues_12_bar(key: str = "C", style: str = "dominant") -> Sequencer:
            """Standard 12-bar blues"""
            progression = ["I"]*4 + ["IV"]*2 + ["I"]*2 + ["V"]*2 + ["IV"] + ["I"] + ["V"]
            return Sequencer.progression(progression, key=key, bpm=120)

    class arpeggios:
        """Common arpeggio patterns"""

        @staticmethod
        def alberti(key: str = "C", octave: int = 4) -> Arpeggiator:
            chord = Chord(f"{key}maj").octave(octave)
            return Arpeggiator(chord, style="alberti", rate="sixteenth")

        @staticmethod
        def rolling(key: str = "Am", octave: int = 4) -> Arpeggiator:
            chord = Chord(f"{key}m").octave(octave)
            return Arpeggiator(chord, style="up-down", rate="eighth")

        @staticmethod
        def broken_chords(key: str = "G", octave: int = 4) -> Arpeggiator:
            chord = Chord(key).octave(octave)
            return Arpeggiator(chord, style="broken", rate="triplet")

    class drums:
        """Enhanced drum presets with more flavor"""

        @staticmethod
        def rock_basic(bpm: int = 120):
            return DrumPattern.basic_rock(bpm=bpm).humanize(time=0.01, velocity=8)

        @staticmethod
        def house_classic(bpm: int = 128):
            beat = DrumPattern.four_on_floor(bpm=bpm)
            beat.open_hihat.on(4, velocity=70)  # Off-beat open hat
            return beat.humanize(time=0.008, velocity=6)

        @staticmethod
        def lofi(bpm: int = 85):
            beat = DrumPattern(bpm=bpm)
            beat.kick.on(1, 3.5).snare.on(2, 4).closed_hihat.eighth(velocity=60)
            return beat.humanize(time=0.025, velocity=12)

        @staticmethod
        def trap_modern(bpm: int = 140):
            beat = DrumPattern.trap(bpm=bpm)
            # Add rolling hi-hats and extra kicks
            beat.closed_hihat.sixteenth(velocity=70)
            beat.kick.on(1, 1.5, 4)
            return beat.humanize(time=0.012, velocity=10)

    class grooves:
        """Full ready-to-play mini arrangements"""

        @staticmethod
        def lofi_chill(key: str = "Cmaj7", bpm: int = 82):
            from .song import Song
            song = Song(bpm=bpm)
            song.add(Presets.drums.lofi(bpm=bpm), channel=9)
            prog = Sequencer.progression(["Cmaj7", "Amin7", "Fmaj7", "G7"], bpm=bpm)
            song.add(prog.arpeggiate(style="up"), channel=1)
            return song.humanize(time=0.04, velocity=15)

        @staticmethod
        def dreamy_arp(key: str = "Fmaj7", bpm: int = 100):
            arp = Arpeggiator(Chord(key).octave(5), style="up-down", rate="triplet")
            return arp.velocity(70).humanize(time=0.03)

        @staticmethod
        def epic_build(key: str = "Dm", bpm: int = 110):
            from .song import Song
            song = Song(bpm=bpm)
            song.add(DrumPattern.basic_rock(bpm=bpm), channel=9)
            song.add(Sequencer.progression(["i", "VI", "III", "VII"], key=key, bpm=bpm))
            return song.humanize(time=0.02)
