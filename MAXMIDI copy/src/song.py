
# src/song.py

from typing import Union, List, Optional
from mido import MidiFile, MidiTrack, Message, MetaMessage
import time
import threading
from .sequencer import Sequencer
from .drums import DrumPattern
from .chord import Chord
from .arpeggiator import Arpeggiator
from .humanize import humanize  # If using the separate humanize module

Playable = Union[Sequencer, DrumPattern, Chord, Arpeggiator]

class Song:
    """
    A multi-track song composer and player.

    Examples:
        song = Song(bpm=110)
        song.add(DrumPattern.basic_rock(), channel=9)  # Drums on channel 10
        song.add(Sequencer.progression(["C", "Am", "F", "G"]))
        song.add(Arpeggiator(Chord("Cmaj7"), style="up-down"), channel=2)
        song.humanize(time=0.03, velocity=12)
        song.play(loop=2)
        song.save("my_jazz_groove.mid")
    """

    def __init__(self, bpm: int = 120, name: str = "Untitled Song"):
        self.bpm = bpm
        self.name = name
        self.tracks: List[dict] = []  # Each: {'playable': Playable, 'channel': int}
        self.length_bars: Optional[int] = None  # Auto-determined or set manually
        self.humanize_time: float = 0.0
        self.humanize_vel: int = 0

    def add(self, playable: Playable, channel: int = 0) -> "Song":
        """
        Add a playable element on a specific MIDI channel (0–15).
        Channel 9 is reserved for drums by convention.
        """
        self.tracks.append({"playable": playable, "channel": channel})
        return self  # Chainable

    def humanize(self, time: float = 0.02, velocity: int = 12) -> "Song":
        """Apply humanization to all tracks"""
        self.humanize_time = time
        self.humanize_vel = velocity
        return self

    def _determine_length(self) -> float:
        """Calculate total duration in seconds based on longest track"""
        max_duration = 0.0
        beat_duration = 60.0 / self.bpm

        for track in self.tracks:
            item = track["playable"]
            if isinstance(item, Sequencer):
                duration = item.total_steps * item.step_duration
            elif isinstance(item, DrumPattern):
                duration = item.steps * (beat_duration / (item.steps // 4))
            elif isinstance(item, (Chord, Arpeggiator)):
                # Assume single event duration ~4 beats if not in sequencer
                duration = 4 * beat_duration
            else:
                duration = 4 * beat_duration
            max_duration = max(max_duration, duration)

        return max_duration or (4 * 4 * beat_duration)  # Default 4 bars

    def play(self, loop: int = 1):
        """Play all tracks simultaneously in separate threads"""
        if not self.tracks:
            print("Warning: Song has no tracks to play.")
            return

        def play_track(track_dict):
            item = track_dict["playable"]
            channel = track_dict["channel"]

            # Apply song-level humanization
            if self.humanize_time or self.humanize_vel:
                if hasattr(item, "humanize"):
                    item.humanize(time=self.humanize_time, velocity=self.humanize_vel)

            # Temporary channel override if needed
            original_channel = None
            if hasattr(item, "channel"):
                original_channel = item.channel
                item.channel = channel

            try:
                if hasattr(item, "play"):
                    item.play(loop=loop)
            finally:
                if original_channel is not None:
                    item.channel = original_channel

        # Start all tracks at the same time
        threads = []
        for track in self.tracks:
            t = threading.Thread(target=play_track, args=(track,))
            t.start()
            threads.append(t)

        # Wait for all to finish
        for t in threads:
            t.join()

    def save(self, filename: str = "song.mid"):
        """Export the song to a Standard MIDI File"""
        mid = MidiFile(ticks_per_beat=480)  # Standard resolution
        midi_tracks = {}

        # Initialize a MIDI track for each channel used
        used_channels = {t["channel"] for t in self.tracks}
        for ch in used_channels:
            mtrack = MidiTrack()
            mtrack.append(MetaMessage('set_tempo', tempo=int(60000000 / self.bpm)))
            if ch == 9:
                mtrack.append(Message('program_change', channel=ch, program=0, time=0))  # Drum channel
            midi_tracks[ch] = mtrack
            mid.tracks.append(mtrack)

        # Helper to add messages with delta time
        def add_messages(mtrack: MidiTrack, messages: List[tuple], start_tick: int = 0):
            current_tick = start_tick
            for msg_type, note, velocity, duration_ticks in messages:
                mtrack.append(Message(msg_type, note=note, velocity=velocity, channel=mtrack_channel, time=current_tick))
                current_tick = duration_ticks
                mtrack.append(Message('note_off', note=note, velocity=0, channel=mtrack_channel, time=current_tick))
                current_tick = 0

        # Collect events from each playable
        ticks_per_quarter = 480
        for track in self.tracks:
            item = track["playable"]
            mtrack_channel = track["channel"]
            mtrack = midi_tracks[mtrack_channel]

            events = []  # List of (type, note, vel, duration_ticks)

            if isinstance(item, Chord):
                duration_beats = 1.0
                for note in item.notes:
                    events.append(('note_on', note.pitch, item.velocity or 100, int(duration_beats * ticks_per_quarter)))
            elif isinstance(item, Arpeggiator):
                # Simplified: export as sequential notes
                arp_notes = item.generate_pattern()  # You may need to expose this
                step_ticks = ticks_per_quarter // 4
                for note in arp_notes:
                    events.append(('note_on', note, 90, step_ticks))
            elif isinstance(item, DrumPattern):
                step_ticks = ticks_per_quarter // 4
                for step, note_num, vel in item.events:
                    tick_offset = step * step_ticks
                    events.append(('note_on', note_num, vel, step_ticks))
            elif isinstance(item, Sequencer):
                # Extract events from sequencer
                step_ticks = ticks_per_quarter * 4 // item.steps_per_bar
                for step, playable, duration in item.events:
                    if playable is None:
                        continue
                    tick_start = step * step_ticks
                    dur_ticks = int(duration * ticks_per_quarter)
                    if isinstance(playable, Chord):
                        for n in playable.notes:
                            events.append(('note_on', n.pitch, 100, dur_ticks))
                    # Add more types as needed

            # Sort by time and add to track
            # For simplicity, assuming sequential for now
            current_time = 0
            for ev in sorted(events, key=lambda x: x[3]):  # Rough sorting
                msg = Message(ev[0], note=ev[1], velocity=ev[2], channel=mtrack_channel, time=current_time)
                mtrack.append(msg)
                current_time = ev[3]
                off = Message('note_off', note=ev[1], velocity=0, channel=mtrack_channel, time=current_time)
                mtrack.append(off)
                current_time = 0

        mid.save(filename)
        print(f"Song saved as '{filename}'")

    def __add__(self, other: Playable) -> "Song":
        """Allow song + playable syntax"""
        self.add(other)
        return self