# -*- coding: utf-8 -*-
"""缩略图内容倾向评分（纯 numpy，无外部模型）：人物肤色占比、清晰度、暗部比例。
输出 tools_cache/people.json: {id: {skin, center_skin, dark, score}}
"""
import os, json, glob
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THUMBS = os.path.join(ROOT, "tools_cache", "thumbs")
OUT = os.path.join(ROOT, "tools_cache", "people.json")


def work(path):
    _id = os.path.splitext(os.path.basename(path))[0]
    try:
        a = np.asarray(Image.open(path).convert("RGB").resize((120, 90)), dtype=np.float32)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        cb = 128 - .168736 * r - .331264 * g + .5 * b
        cr = 128 + .5 * r - .418688 * g - .081312 * b
        skin = ((cr > 132) & (cr < 182) & (cb > 76) & (cb < 132) &
                (r > 90) & (g > 35) & (b > 15) & (r > g * 1.05) & (r > b * 1.08))
        y = .299 * r + .587 * g + .114 * b
        dark = float((y < 46).mean())
        s = float(skin.mean())
        cs = float(skin[12:78, 18:102].mean())
        # 人物倾向：肤色占比适中且集中在画面中部更好
        person = min(s / .16, 1.0) * 6 + min(cs / .22, 1.0) * 4
        return _id, {"skin": round(s, 4), "center_skin": round(cs, 4),
                     "dark": round(dark, 3), "person": round(person, 2)}
    except Exception:
        return _id, {"skin": 0, "center_skin": 0, "dark": 1, "person": 0}


def main():
    paths = sorted(glob.glob(os.path.join(THUMBS, "*.jpg")))
    print("thumbs:", len(paths), flush=True)
    out = {}
    for i, p in enumerate(paths, 1):
        k, v = work(p)
        out[k] = v
        if i % 2000 == 0:
            print(" ", i, flush=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f)
    print("person>=5:", sum(1 for v in out.values() if v["person"] >= 5), flush=True)
    print("person>=8:", sum(1 for v in out.values() if v["person"] >= 8), flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
