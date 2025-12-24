# ---------------------------------------------------------------------------
#  CMaxMidiTrack (Python Rewrite using struct)
#
#  Original C++ Version:
#  (C) Copyright, Paul A. Messick, 1996
#
#  Python Rewrite:
#  Clean-room reimplementation preserving structure and behavior of the
#  original Win32/MFC MIDI track engine. Intended for educational,
#  archival, and interoperability use.
# ---------------------------------------------------------------------------

import ctypes

# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------
DEFAULT_BUFFER_SIZE = 8192
BUFFER_GROW_SIZE = DEFAULT_BUFFER_SIZE

# ------------------------------------------------------------
# MidiEvent struct (ctypes version)
# ------------------------------------------------------------
class MidiEvent(ctypes.Structure):
    _fields_ = [
        ("time", ctypes.c_uint32),
        ("status", ctypes.c_uint32),
        ("data1", ctypes.c_uint32),
        ("data2", ctypes.c_uint32),
    ]

    def __init__(self, time=0, status=0, data1=0, data2=0):
        super().__init__(time, status, data1, data2)

# ------------------------------------------------------------
# CMaxMidiTrack struct-backed class
# ------------------------------------------------------------
class CMaxMidiTrack:
    def __init__(self):
        self.dwBufSize = DEFAULT_BUFFER_SIZE
        self.inPtr = 0
        self.outPtr = 0
        self.fRecord = False
        self.fMute = False
        self.lpName = None

        # Optional attachments
        self.pSMF = None
        self.pMidiOut = None
        self.pMidiIn = None

        # Allocate buffer array
        self.lpBuffer = (MidiEvent * self.dwBufSize)()

    # --------------------------------------------------------
    # Destructor-style cleanup
    # --------------------------------------------------------
    def __del__(self):
        self.Detach()
        self.FreeBuffer()

    # --------------------------------------------------------
    # Attach / Detach
    # --------------------------------------------------------
    def AttachSMF(self, smf):
        self.pSMF = smf

    def AttachMidiOut(self, midi_out):
        self.pMidiOut = midi_out

    def AttachMidiIn(self, midi_in):
        self.pMidiIn = midi_in

    def Detach(self):
        self.pSMF = None
        self.pMidiOut = None
        self.pMidiIn = None
        self.fRecord = False

    # --------------------------------------------------------
    # State
    # --------------------------------------------------------
    def IsEmpty(self):
        return (self.inPtr - self.outPtr) == 0

    def IsRecording(self):
        return self.fRecord

    def SetRecording(self, record):
        self.fRecord = record

    def Mute(self, mute=None):
        if mute is None:
            return self.fMute
        self.fMute = mute

    # --------------------------------------------------------
    # Buffer management
    # --------------------------------------------------------
    def FreeBuffer(self):
        self.lpBuffer = (MidiEvent * 0)()
        self.dwBufSize = 0
        self.inPtr = 0
        self.outPtr = 0

    def GetBufferSize(self):
        return self.dwBufSize

    def GetNumEvents(self):
        return self.inPtr - self.outPtr

    def Flush(self):
        self.inPtr = self.outPtr = 0

    def Rewind(self):
        self.outPtr = 0

    # --------------------------------------------------------
    # Event access
    # --------------------------------------------------------
    def GetEvent(self, eventNum):
        if eventNum >= self.inPtr:
            return None
        return self.lpBuffer[eventNum]

    def SetEvent(self, event, eventNum):
        if eventNum < self.dwBufSize:
            self.lpBuffer[eventNum] = event

    def GetTime(self, eventNum):
        if eventNum >= self.inPtr:
            return 0
        return self.lpBuffer[eventNum].time

    # --------------------------------------------------------
    # Read / Write
    # --------------------------------------------------------
    def Read(self):
        if self.outPtr == self.inPtr or self.fMute or self.fRecord:
            return None
        ev = self.lpBuffer[self.outPtr]
        self.outPtr += 1
        return ev

    def Write(self, event):
        if not self.fRecord:
            return
        self.InsertEvent(event, -1)

    # --------------------------------------------------------
    # Editing
    # --------------------------------------------------------
    def _grow(self):
        new_buf = (MidiEvent * (self.dwBufSize + BUFFER_GROW_SIZE))()
        ctypes.memmove(new_buf, self.lpBuffer, ctypes.sizeof(self.lpBuffer))
        self.lpBuffer = new_buf
        self.dwBufSize += BUFFER_GROW_SIZE

    def InsertEvent(self, event, beforeEvent):
        if self.inPtr == self.dwBufSize:
            self._grow()

        if beforeEvent == -1 or beforeEvent >= self.inPtr:
            self.lpBuffer[self.inPtr] = event
            self.inPtr += 1
            return

        # Shift elements
        for i in range(self.inPtr, beforeEvent, -1):
            self.lpBuffer[i] = self.lpBuffer[i - 1]
        self.lpBuffer[beforeEvent] = event
        self.inPtr += 1

    def DeleteEvent(self, eventNum):
        if eventNum < self.inPtr:
            for i in range(eventNum, self.inPtr - 1):
                self.lpBuffer[i] = self.lpBuffer[i + 1]
            self.inPtr -= 1

    def SlideTrack(self, eventNum, delta):
        if eventNum < self.inPtr:
            self.lpBuffer[eventNum].time = max(
                0, self.lpBuffer[eventNum].time + delta
            )

    # --------------------------------------------------------
    # Absolute / Delta Time
    # --------------------------------------------------------
    def AbsNow(self, eventNum):
        if eventNum >= self.inPtr:
            return 0
        total = 0
        for i in range(eventNum + 1):
            total += self.lpBuffer[i].time
        return total

    def DeltaToAbs(self, buf, startEvent, numEvents):
        now = self.AbsNow(startEvent)
        buf[0].time = now
        for i in range(1, numEvents):
            now += buf[i].time
            buf[i].time = now

    def AbsToDelta(self, buf, startEvent, numEvents):
        start = 0 if startEvent == 0 else self.AbsNow(startEvent - 1)
        for i in range(numEvents):
            now = buf[i].time
            buf[i].time -= start
            start = now

    def GetAbsBuffer(self, startEvent, numEvents):
        if startEvent >= self.inPtr or self.fMute or self.fRecord:
            return []

        count = min(self.inPtr - startEvent, numEvents)
        buf = [(self.lpBuffer[startEvent + i]) for i in range(count)]
        self.DeltaToAbs(buf, startEvent, count)
        return buf