import ctypes, json, urllib.request
from ctypes import wintypes as w
u32 = ctypes.WinDLL("user32")
u32.GetWindowTextW.argtypes = [w.HWND, w.LPWSTR, ctypes.c_int]

def wins():
    out = []
    @ctypes.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
    def cb(h, _):
        n = ctypes.create_unicode_buffer(300)
        u32.GetWindowTextW(h, n, 300)
        if n.value: out.append([int(h), n.value])
        return True
    u32.EnumWindows(cb, 0)
    return out

def probe():
    p = {"bluebook": any("bluebook" in t.lower() for _, t in wins()), "cdp": False}
    try:
        urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=2); p["cdp"] = True
    except Exception:
        pass
    return p

CF = 13
def set_clip(s):
    u32.OpenClipboard(None)
    try:
        u32.EmptyClipboard()
        u32.SetClipboardData(CF, ctypes.create_unicode_buffer(s))
    finally: u32.CloseClipboard()

def get_clip():
    u32.OpenClipboard(None)
    try:
        if not u32.IsClipboardFormatAvailable(CF): return ""
        return ctypes.wstring_at(u32.GetClipboardData(CF))
    finally: u32.CloseClipboard()