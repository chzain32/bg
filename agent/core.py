import asyncio, hmac, json, os, time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse, JSONResponse
import hid, capture, covert, health

TOKEN = os.environ["GHOST_TOKEN"]
app = FastAPI()
grab = capture.Grabber()
subs: set = set()
state = {"roi": None, "q": 68, "paused": False}

def auth(t): return hmac.compare_digest(t or "", TOKEN)

@app.get("/", response_class=HTMLResponse)
def idx():
    p = os.path.join(os.path.dirname(__file__), "..", "client", "panel.html")
    return open(p, encoding="utf-8").read()

@app.get("/health")
def healthz(t: str = Query("")): return JSONResponse({"ok": auth(t)})

@app.on_event("startup")
async def boot():
    async def loop():
        while True:
            if state["paused"] or not subs:
                await asyncio.sleep(0.2); continue
            f = await asyncio.to_thread(grab.frame, state["roi"], state["q"])
            if f:
                if not health.check(f, len(subs)):
                    os._exit(1)
                for ws in list(subs):
                    try: await ws.send_bytes(b"\x01" + f)
                    except Exception: subs.discard(ws)
            await asyncio.sleep(0.06)
    asyncio.create_task(loop())

def do(c, a):
    if c == "move": hid.move(a["x"], a["y"])
    elif c == "click": hid.move(a["x"], a["y"]); hid.click(a.get("b", "left"), a.get("n", 1))
    elif c == "down": hid.move(a["x"], a["y"]); hid.mdown(a.get("b", "left"))
    elif c == "up": hid.mup(a.get("b", "left"))
    elif c == "wheel": hid.wheel(a["d"])
    elif c == "drag": hid.drag(a["x1"], a["y1"], a["x2"], a["y2"])
    elif c == "text": hid.type_text(a["t"])
    elif c == "key": hid.hotkey(*a["v"])
    elif c == "kd": hid.kd(a["v"])
    elif c == "ku": hid.ku(a["v"])
    elif c == "roi": state["roi"] = tuple(a["r"]) if a.get("r") else None; return "ok"
    elif c == "q": state["q"] = int(a["v"]); return "ok"
    elif c == "pause": state["paused"] = bool(a["v"]); return "ok"
    elif c == "fg": hid.force_fg(a["h"]); return "ok"
    elif c == "wins": return covert.wins()
    elif c == "probe": return covert.probe()
    elif c == "clip": covert.set_clip(a["t"]); return "ok"
    elif c == "clipget": return covert.get_clip()
    elif c == "size": return list(grab.size())
    elif c == "ping": return int(time.time() * 1000)
    return "ok"

@app.websocket("/ws")
async def ws(sock: WebSocket, t: str = Query("")):
    if not auth(t): await sock.close(code=4401); return
    await sock.accept(); subs.add(sock)
    try:
        while True:
            m = json.loads(await sock.receive_text())
            r = await asyncio.to_thread(do, m.get("c"), m.get("a", {}))
            if m.get("id"): await sock.send_text(json.dumps({"id": m["id"], "r": r}))
    except WebSocketDisconnect:
        subs.discard(sock)