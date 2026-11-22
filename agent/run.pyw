import os, sys, secrets, ctypes
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ctypes.windll.shcore.SetProcessDpiAwareness(2)
if not os.environ.get("GHOST_TOKEN"):
    os.environ["GHOST_TOKEN"] = secrets.token_urlsafe(32)
    open(os.path.join(os.environ["LOCALAPPDATA"], "ghost.token"), "w").write(os.environ["GHOST_TOKEN"])
import logging; logging.disable(logging.CRITICAL)
import uvicorn
from agent.core import app
uvicorn.run(app, host=os.environ.get("GHOST_HOST", "0.0.0.0"),
            port=int(os.environ.get("GHOST_PORT", 8731)),
            log_level="critical", access_log=False)