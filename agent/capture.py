"""DXGI primary, GDI fallback. ROI crops stay at native pixels; 4:4:4 JPEG
so small text survives."""
import ctypes, io, hashlib
from ctypes import wintypes as w
from PIL import Image

u32, g32 = ctypes.WinDLL("user32"), ctypes.WinDLL("gdi32")
SRCCOPY, DIB = 0x00CC0020, 0

class BIH(ctypes.Structure):
    _fields_ = [("s", w.DWORD), ("w", w.LONG), ("h", w.LONG), ("p", w.WORD),
                ("b", w.WORD), ("c", w.DWORD), ("si", w.DWORD), ("xp", w.LONG),
                ("yp", w.LONG), ("cu", w.DWORD), ("ci", w.DWORD)]

class BI(ctypes.Structure):
    _fields_ = [("h", BIH), ("col", w.DWORD * 3)]

class Grabber:
    def __init__(self, max_w=1500, quality=68):
        self.max_w, self.q = max_w, quality
        self.desktop = u32.GetDesktopWindow()
        self._sig = b""
        self.cam = None
        try:
            import dxcam
            self.cam = dxcam.create(output_idx=0, output_color="RGB")
            self.cam.grab()
        except Exception:
            self.cam = None

    def size(self):
        r = w.RECT(); u32.GetWindowRect(self.desktop, ctypes.byref(r))
        return r.right - r.left, r.bottom - r.top

    def _full(self):
        sw, sh = self.size()
        sdc = u32.GetWindowDC(self.desktop)
        mdc = g32.CreateCompatibleDC(sdc)
        bi = BI(); bi.h.s = ctypes.sizeof(BIH); bi.h.w, bi.h.h = sw, -sh
        bi.h.p, bi.h.b = 1, 32
        bits = ctypes.c_void_p()
        bmp = g32.CreateDIBSection(sdc, ctypes.byref(bi), DIB, ctypes.byref(bits), None, 0)
        g32.SelectObject(mdc, bmp)
        g32.BitBlt(mdc, 0, 0, sw, sh, sdc, 0, 0, SRCCOPY)
        buf = ctypes.string_at(bits, sw * sh * 4)
        g32.DeleteObject(bmp); g32.DeleteDC(mdc); u32.ReleaseDC(self.desktop, sdc)
        return Image.frombuffer("RGB", (sw, sh), buf, "raw", "BGRX", 0, 1)

    def frame(self, roi=None, quality=None, force=False):
        img = None
        if self.cam is not None:
            try:
                a = self.cam.grab()
                if a is not None: img = Image.fromarray(a)
            except Exception:
                pass
        if img is None:
            img = self._full()
        if roi:
            x, y, ww, hh = (int(v) for v in roi)
            img = img.crop((x, y, x + max(ww, 1), y + max(hh, 1)))
        if img.width > self.max_w:
            img = img.resize((self.max_w, round(img.height * self.max_w / img.width)), Image.LANCZOS)
        b = io.BytesIO()
        img.save(b, "JPEG", quality=int(quality or self.q), subsampling=0)
        d = b.getvalue()
        sig = hashlib.blake2b(d, digest_size=8).digest()
        if sig == self._sig and not force: return None
        self._sig = sig
        return d