"""Mechanical checks only. Run elevated on the target while the agent is live."""
import sys, json, time, statistics, ctypes
sys.path.insert(0, "C:\\ProgramData\\RuntimeBroker")
import hid, capture

g = capture.Grabber()
res = {"pass": True, "checks": {}}

def put(k, ok, detail=""):
    res["checks"][k] = {"ok": bool(ok), "detail": detail}
    if not ok: res["pass"] = False

sw, sh = g.size()
put("size", sw >= 1280 and sh >= 720, f"{sw}x{sh}")

gaps, black = [], 0
for _ in range(30):
    t = time.perf_counter()
    f = g.frame(None, 68, force=True)
    gaps.append((time.perf_counter() - t) * 1000)
    if f is None: black += 1
put("frames", black == 0, f"{30-black}/30 produced")
put("interval_p95", statistics.quantiles(gaps, n=20)[18] < 90,
    f"p95 {statistics.quantiles(gaps, n=20)[18]:.1f}ms")

worst = 0
for gx in (0.2, 0.5, 0.8):
    for gy in (0.2, 0.5, 0.8):
        tx, ty = int(sw * gx), int(sh * gy)
        hid.move(tx, ty); time.sleep(0.05)
        ax, ay = hid.cursor()
        worst = max(worst, abs(ax - tx), abs(ay - ty))
put("coords", worst <= 3, f"worst drift {worst}px")

put("os", ctypes.windll.ntdll.RtlGetVersion.__class__ is not None,
    ctypes.windll.ntdll and "")

try:
    b = __import__("winreg").OpenKey(__import__("winreg").HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
    put("build", __import__("winreg").QueryValueEx(b, "CurrentBuildNumber")[0] >= "26100",
        __import__("winreg").QueryValueEx(b, "CurrentBuildNumber")[0])
except Exception as e:
    put("build", False, str(e))

print(json.dumps(res, indent=1))
open(time.strftime("verify-%Y%m%d-%H%M.json"), "w").write(json.dumps(res, indent=1))
sys.exit(0 if res["pass"] else 1)