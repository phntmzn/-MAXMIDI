# ---------------------------------------------------------------------------
#  CMaxMidiSync (Python Rewrite using struct)
#
#  Original C++ Version:
#  (C) Copyright, Paul A. Messick, 1996
#
#  Python Rewrite:
#  This code is a faithful structural and behavioral translation of the
#  original MFC/Win32 implementation for educational, archival, and
#  interoperability purposes.
#
#  No original source code has been copied verbatim; this is a clean
#  reimplementation based on publicly visible interfaces and behavior.
# ---------------------------------------------------------------------------

import ctypes

# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------
MXMIDIERR_MAXERR = 0
USE_CURRENT = 0xFFFF
S_INT = 0x0001  # internal sync mode

# ------------------------------------------------------------
# Mock low-level Sync API (C-style stubs)
# ------------------------------------------------------------
def OpenSync(handle, hwnd, mode, period):
    return 1  # fake device handle

def CloseSync(handle):
    pass

def StartSync(handle):
    pass

def ReStartSync(handle):
    pass

def StopSync(handle):
    pass

def PauseSync(handle, reset):
    pass

def SetTempo(handle, tempo):
    return 0

def GetTempo(handle):
    return 500000  # default µs/beat (120 BPM)

def SetResolution(handle, res):
    pass

def GetResolution(handle):
    return 96

# ------------------------------------------------------------
# CMaxMidiSync using ctypes
# ------------------------------------------------------------
class CMaxMidiSyncStruct(ctypes.Structure):
    _fields_ = [
        ("hDevice", ctypes.c_uint16),
        ("fIsOpen", ctypes.c_bool),
        ("fRunning", ctypes.c_bool),
        ("current_mode", ctypes.c_uint16),
        ("current_period", ctypes.c_uint16),
    ]

class CMaxMidiSync:
    def __init__(self, parent_wnd=None, mode=None, timer_period=None):
        self.hParentWnd = parent_wnd
        self.m_hWnd = id(self)
        self._state = CMaxMidiSyncStruct(
            hDevice=0,
            fIsOpen=False,
            fRunning=False,
            current_mode=0,
            current_period=0
        )

        if mode is not None:
            self.Open(mode, timer_period or 10)

    # --------------------------------------------------------
    # State queries
    # --------------------------------------------------------
    def IsOpen(self):
        return self._state.fIsOpen

    def IsRunning(self):
        return self._state.fRunning

    def GetHSync(self):
        return self._state.hDevice

    def Mode(self):
        return self._state.current_mode

    def Period(self):
        return self._state.current_period

    # --------------------------------------------------------
    # Open / Close
    # --------------------------------------------------------
    def Open(self, mode=S_INT, timer_period=10):
        if not self._state.fIsOpen:
            hDevice = OpenSync(0, self.m_hWnd, mode, timer_period)
            if hDevice > MXMIDIERR_MAXERR:
                self._state.hDevice = hDevice
                self._state.fIsOpen = True
                self._state.fRunning = False
                self._state.current_mode = mode
                self._state.current_period = timer_period
                return True

        self._state = CMaxMidiSyncStruct()
        return False

    def Close(self):
        if self._state.fIsOpen:
            CloseSync(self._state.hDevice)
        self._state = CMaxMidiSyncStruct()

    # --------------------------------------------------------
    # Mode / Period
    # --------------------------------------------------------
    def SetMode(self, mode):
        if self._state.fIsOpen:
            hDevice = OpenSync(self._state.hDevice, self.m_hWnd, mode, USE_CURRENT)
            if hDevice > MXMIDIERR_MAXERR:
                self._state.hDevice = hDevice
                self._state.current_mode = mode
                return True
        self._state = CMaxMidiSyncStruct()
        return False

    def SetPeriod(self, period):
        if self._state.fIsOpen:
            hDevice = OpenSync(self._state.hDevice, self.m_hWnd, USE_CURRENT, period)
            if hDevice > MXMIDIERR_MAXERR:
                self._state.hDevice = hDevice
                self._state.current_period = period
                return True
        self._state = CMaxMidiSyncStruct()
        return False

    # --------------------------------------------------------
    # Start / Stop / Pause
    # --------------------------------------------------------
    def Start(self):
        if self._state.fIsOpen:
            StartSync(self._state.hDevice)
            self._state.fRunning = True

    def ReStart(self):
        if self._state.fIsOpen:
            ReStartSync(self._state.hDevice)
            self._state.fRunning = True

    def Stop(self):
        if self._state.fIsOpen:
            StopSync(self._state.hDevice)
            self._state.fRunning = False

    def Pause(self, reset=False):
        if self._state.fIsOpen:
            PauseSync(self._state.hDevice, reset)
            self._state.fRunning = False

    # --------------------------------------------------------
    # Tempo / Resolution
    # --------------------------------------------------------
    def Tempo(self, tempo=None):
        hDevice = self.GetHSync()
        if tempo is None:
            return GetTempo(hDevice)
        return SetTempo(hDevice, tempo) == 0

    def Resolution(self, res=None):
        hDevice = self.GetHSync()
        if res is None:
            return GetResolution(hDevice)
        SetResolution(hDevice, res)

    # --------------------------------------------------------
    # Tempo Conversion
    # --------------------------------------------------------
    def Convert(self, value):
        if isinstance(value, float):
            if value == 0.0:
                value = 120.0
            return int(60000000.0 / value)
        return 60000000.0 / float(value)

    # --------------------------------------------------------
    # Overridable hooks
    # --------------------------------------------------------
    def ProcessMidiBeat(self):
        pass

    def ProcessSyncDone(self):
        pass