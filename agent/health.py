"""Black-frame watchdog: three consecutive near-black reads with a live
viewer means capture is dead, so exit non-zero and let the task restart us."""
import io
from PIL import Image, ImageStat

_black = 0

def check(jpeg, viewers: int) -> bool:
    global _black
    if not jpeg or viewers == 0:
        _black = 0
        return True
    mean = ImageStat.Stat(Image.open(io.BytesIO(jpeg)).convert("L")).mean[0]
    _black = _black + 1 if mean < 4 else 0
    return _black < 3