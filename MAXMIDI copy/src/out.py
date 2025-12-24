# ---------------------------------------------------------------------------
#  MaxMidiOut – Python struct-based rewrite
#
#  (C) Copyright, Paul A. Messick, 1996
#  Python rewrite using struct module
# ---------------------------------------------------------------------------

import ctypes
from typing import List

# ---------------------------------------------------------------------------
# MIDI constants
# ---------------------------------------------------------------------------
SYSEX = 0xF0
EOX   = 0xF7
MERGE_BUFFER_SIZE = 512

# ---------------------------------------------------------------------------
# MidiEvent struct (C-style)
# struct MidiEvent { DWORD time; BYTE status; BYTE data1; BYTE data2; }
# ---------------------------------------------------------------------------
class MidiEvent(ctypes.Structure):
    _fields_ = [
        ("time", ctypes.c_uint32),
        ("status", ctypes.c_uint8),
        ("data1", ctypes.c_uint8),
        ("data2", ctypes.c_uint8),
    ]

    def __init__(self, time=0, status=0, data1=0, data2=0):
        super().__init__(time, status, data1, data2)

# ---------------------------------------------------------------------------
# TrackMerge struct (Python container)
# ---------------------------------------------------------------------------
class TrackMerge(ctypes.Structure):
    _fields_ = [
        ("track", ctypes.c_void_p),  # abstract track reference
        ("abs_buffer", ctypes.POINTER(MidiEvent)),
        ("buf_size", ctypes.c_int),
        ("this_event", ctypes.c_int),
        ("last_event", ctypes.c_int),
        ("in_sysex", ctypes.c_int),  # bool
    ]

    def __init__(self, track=None):
        super().__init__()
        self.track = ctypes.cast(track, ctypes.c_void_p) if track else None
        self.abs_buffer = None
        self.buf_size = MERGE_BUFFER_SIZE
        self.this_event = 0
        self.last_event = 0
        self.in_sysex = 0

# ---------------------------------------------------------------------------
# CMaxMidiOutState struct (Python container)
# ---------------------------------------------------------------------------
class CMaxMidiOutState(ctypes.Structure):
    _fields_ = [
        ("device_id", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("is_open", ctypes.c_int),      # bool
        ("description", ctypes.c_char * 32),
        ("last_abs", ctypes.c_uint32),
        ("tracks", ctypes.POINTER(TrackMerge)),
        ("num_tracks", ctypes.c_int),
        ("merge_buffer", ctypes.POINTER(MidiEvent)),
        ("merge_size", ctypes.c_int),
        ("out_ptr", ctypes.c_int),
    ]

    def __init__(self):
        super().__init__()
        self.device_id = 0
        self.flags = 0
        self.is_open = 0
        self.description = b""
        self.last_abs = 0
        self.tracks = None
        self.num_tracks = 0
        self.merge_buffer = None
        self.merge_size = 0
        self.out_ptr = 0

# ---------------------------------------------------------------------------
# Track merge logic
# ---------------------------------------------------------------------------
def merge_tracks(state: CMaxMidiOutState) -> List[MidiEvent]:
    merged = []
    any_sysex = False
    sysex_track = None

    tracks = [state.tracks[i] for i in range(state.num_tracks)]

    # Load buffers
    for tm in tracks:
        # Call the abstract track's get_abs_buffer (requires proper ctypes wrapper)
        if tm.track:
            # Assuming the track object has a get_abs_buffer() returning a Python list
            abs_buf = tm.track.contents.get_abs_buffer(tm.last_event, tm.buf_size)
            buf_type = MidiEvent * len(abs_buf)
            tm.abs_buffer = buf_type(*abs_buf)
            tm.this_event = 0

            if tm.in_sysex and len(abs_buf):
                any_sysex = True
                sysex_track = tm

    while len(merged) < MERGE_BUFFER_SIZE:
        candidate = None
        candidate_track = None

        for tm in tracks:
            if not tm.abs_buffer or tm.this_event >= tm.buf_size:
                continue
            ev = tm.abs_buffer[tm.this_event]
            if candidate is None or ev.time < candidate.time:
                if not any_sysex or tm is sysex_track:
                    candidate = ev
                    candidate_track = tm

        if candidate is None:
            break

        merged.append(candidate)
        candidate_track.this_event += 1

        if candidate.data1 == SYSEX:
            candidate_track.in_sysex = 1
            any_sysex = True
            sysex_track = candidate_track
        elif candidate.data1 == EOX:
            candidate_track.in_sysex = 0
            any_sysex = False
            sysex_track = None

    # Update track positions
    for tm in tracks:
        tm.last_event += tm.this_event

    # Convert absolute → delta time
    if merged:
        new_last_abs = merged[-1].time
        for i in range(len(merged) - 1, 0, -1):
            merged[i].time -= merged[i - 1].time
            if merged[i].time < 0:
                merged[i].time = 0
        merged[0].time -= state.last_abs
        state.last_abs = new_last_abs

    # Assign merge buffer back to state
    merge_type = MidiEvent * len(merged)
    state.merge_buffer = merge_type(*merged)
    state.merge_size = len(merged)
    state.out_ptr = 0
    return merged

# ---------------------------------------------------------------------------
# Output pumping
# ---------------------------------------------------------------------------
def merge_out(state: CMaxMidiOutState, put_func):
    if state.num_tracks == 0:
        return
    if state.out_ptr >= state.merge_size:
        merge_tracks(state)
    while state.out_ptr < state.merge_size:
        ev = state.merge_buffer[state.out_ptr]
        if not put_func(ev):
            break
        state.out_ptr += 1

# ---------------------------------------------------------------------------
# Example MIDI output stub
# ---------------------------------------------------------------------------
def put_midi_out(event: MidiEvent) -> bool:
    # Here you'd call ctypes-wrapped library function
    raw_bytes = bytes(ctypes.string_at(ctypes.byref(event), ctypes.sizeof(event)))
    return True