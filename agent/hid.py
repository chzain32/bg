"""Scancode injection. Bluebook installs no hook, but scancodes are correct
regardless and survive any future filter."""
import ctypes, time
from ctypes import wintypes as w

u32 = ctypes.WinDLL("user32", use_last_error=True)
P = ctypes.c_size_t
SC, KU, EXT, KBD, MOU = 0x0008, 0x0002, 0x0001, 1, 0
LD, LU, RD, RU, MD, MU, WH = 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x0800

class MI(ctypes.Structure):
    _fields_ = [("dx", w.LONG), ("dy", w.LONG), ("data", w.DWORD),
                ("flags", w.DWORD), ("time", w.DWORD), ("extra", P)]

class KI(ctypes.Structure):
    _fields_ = [("vk", w.WORD), ("scan", w.WORD), ("flags", w.DWORD),
                ("time", w.DWORD), ("extra", P)]

class _U(ctypes.Union):
    _fields_ = [("mi", MI), ("ki", KI)]

class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", w.DWORD), ("u", _U)]

u32.SendInput.argtypes = [w.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
u32.SendInput.restype = w.UINT
u32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
u32.SetCursorPos.restype = w.BOOL
u32.MapVirtualKeyW.argtypes = [w.UINT, w.UINT]
u32.MapVirtualKeyW.restype = w.UINT
u32.VkKeyScanW.argtypes = [w.WCHAR]
u32.VkKeyScanW.restype = ctypes.c_short

def _send(*i):
    a = (INPUT * len(i))(*i)
    u32.SendInput(len(i), a, ctypes.sizeof(INPUT))

def _sc(vk): return u32.MapVirtualKeyW(vk, 0) or vk

def kd(vk, ext=False):
    i = INPUT(type=KBD); i.ki = KI(0, _sc(vk), SC | (EXT if ext else 0), 0, 0); _send(i)

def ku(vk, ext=False):
    i = INPUT(type=KBD); i.ki = KI(0, _sc(vk), SC | KU | (EXT if ext else 0), 0, 0); _send(i)

def tap(vk, ext=False):
    kd(vk, ext); time.sleep(0.008); ku(vk, ext)

def hotkey(*vks):
    for v in vks: kd(v)
    for v in reversed(vks): ku(v)

def type_text(s, delay=0.005):
    for ch in s:
        r = u32.VkKeyScanW(ch)
        if r == -1: continue
        vk, sh = r & 0xFF, (r >> 8) & 1
        if sh: kd(0x10)
        tap(vk)
        if sh: ku(0x10)
        time.sleep(delay)

def move(x, y): u32.SetCursorPos(int(x), int(y))

def cursor():
    p = w.POINT(); u32.GetCursorPos(ctypes.byref(p)); return p.x, p.y

def mdown(b="left"):
    i = INPUT(type=MOU); i.mi = MI(0, 0, 0, {"left": LD, "right": RD, "middle": MD}[b], 0, 0); _send(i)

def mup(b="left"):
    i = INPUT(type=MOU); i.mi = MI(0, 0, 0, {"left": LU, "right": RU, "middle": MU}[b], 0, 0); _send(i)

def click(b="left", n=1):
    for _ in range(n):
        mdown(b); time.sleep(0.02); mup(b); time.sleep(0.05)

def wheel(d):
    i = INPUT(type=MOU); i.mi = MI(0, 0, d, WH, 0, 0); _send(i)

def drag(x1, y1, x2, y2, steps=20):
    move(x1, y1); time.sleep(0.04); mdown()
    for k in range(1, steps + 1):
        move(x1 + (x2 - x1) * k / steps, y1 + (y2 - y1) * k / steps); time.sleep(0.008)
    mup()

def force_fg(hwnd):
    fg = u32.GetForegroundWindow()
    tf = u32.GetWindowThreadProcessId(fg, None)
    tm = ctypes.windll.kernel32.GetCurrentThreadId()
    u32.AttachThreadInput(tm, tf, True)
    u32.BringWindowToTop(w.HWND(hwnd)); u32.SetForegroundWindow(w.HWND(hwnd))
    u32.AttachThreadInput(tm, tf, False)