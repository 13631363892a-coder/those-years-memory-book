# -*- coding: utf-8 -*-
"""快速照片索引：只读文件头部 + EXIF 内嵌缩略图，不修改任何原始照片。
输出: tools_cache/photo-index.json, tools_cache/thumbs/<id>.jpg, tools_cache/report.txt
"""
import os, sys, json, io, hashlib, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import Counter, defaultdict
from PIL import Image
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from photo_tools import parse_head, thumb_image

SRC = r"F:\佳能\初中"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "tools_cache")
THUMBS = os.path.join(CACHE, "thumbs")
EXTS = {".jpg", ".jpeg", ".png"}


def pid(rel):
    return hashlib.md5(rel.replace("\\", "/").encode("utf-8")).hexdigest()[:12]


def bits_to_hex(bits):
    return "".join("1" if b else "0" for b in bits)


def work(args):
    path, rel = args
    _id = pid(rel)
    rec = {"id": _id, "p": rel, "ok": False}
    try:
        info = parse_head(path)
        rec["w"], rec["h"] = info.get("w", 0), info.get("h", 0)
        rec["bytes"] = info.get("bytes", 0)
        rec["fmt"] = info.get("fmt")
        rec["dt"] = info.get("exif_dt")
        rec["camera"] = info.get("camera")
        rec["orient"] = info.get("orient", 1)
        rec["mtime"] = os.stat(path).st_mtime
        parts = rel.replace("\\", "/").split("/")
        rec["section"] = parts[0] if len(parts) > 1 else "(root)"
        rec["folder"] = "/".join(parts[:-1])
        if rec["dt"] and len(rec["dt"]) >= 7:
            rec["month"] = rec["dt"][:7].replace(":", "-")
        th = thumb_image(info)
        if th is None:
            # 没有内嵌缩略图：完整解码兜底（数量通常很少）
            try:
                with Image.open(path) as im:
                    im.draft("RGB", (320, 320))
                    th = im.convert("RGB")
                    th.thumbnail((320, 320), Image.Resampling.BILINEAR)
            except Exception:
                th = None
        if th is not None:
            os.makedirs(THUMBS, exist_ok=True)
            th.save(os.path.join(THUMBS, _id + ".jpg"), quality=82)
            arr = np.asarray(th.resize((96, 72), Image.Resampling.BILINEAR), dtype=np.float32)
            gray = arr[..., 0] * .299 + arr[..., 1] * .587 + arr[..., 2] * .114
            lap = (-4 * gray[1:-1, 1:-1] + gray[:-2, 1:-1] + gray[2:, 1:-1]
                   + gray[1:-1, :-2] + gray[1:-1, 2:])
            rec["sharp"] = round(float(lap.var()), 1)
            rec["bright"] = round(float(gray.mean()), 1)
            rec["contrast"] = round(float(gray.std()), 1)
            rec["warm"] = round(float((arr[..., 0] - arr[..., 2]).mean()), 1)
            g = np.asarray(th.convert("L").resize((17, 16), Image.Resampling.BILINEAR))
            rec["dhash"] = bits_to_hex((g[:, 1:] > g[:, :-1]).flatten())
            tiny = np.asarray(th.resize((8, 8), Image.Resampling.BILINEAR), dtype=np.float32)
            rec["sig"] = [round(float(v), 0) for v in tiny.flatten()]
        rec["ok"] = True
    except Exception as e:
        rec["err"] = str(e)[:150]
    return rec


def main():
    t0 = time.time()
    pairs = []
    for root, dirs, files in os.walk(SRC):
        for fn in files:
            if os.path.splitext(fn)[1].lower() in EXTS:
                full = os.path.join(root, fn)
                pairs.append((full, os.path.relpath(full, SRC)))
    print(f"found {len(pairs)} images", flush=True)
    os.makedirs(CACHE, exist_ok=True)
    os.makedirs(THUMBS, exist_ok=True)
    results = []
    n = 0
    with ProcessPoolExecutor(max_workers=10) as pool:
        for rec in pool.map(work, pairs, chunksize=20):
            results.append(rec)
            n += 1
            if n % 1000 == 0:
                print(f"  {n}/{len(pairs)}  {round(time.time()-t0,1)}s", flush=True)
    results.sort(key=lambda r: r["p"])
    with open(os.path.join(CACHE, "photo-index.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, separators=(",", ":"))

    ok = [r for r in results if r.get("ok")]
    bad = [r for r in results if not r.get("ok")]
    lines = []
    lines.append(f"总图片数: {len(results)}  可解析: {len(ok)}  失败: {len(bad)}")
    lines.append(f"总容量: {sum(r.get('bytes',0) for r in ok)/1024**3:.2f} GB")
    lines.append(f"格式: {Counter(r.get('fmt') for r in ok).most_common()}")
    lines.append(f"分辨率 TOP: {Counter((r.get('w'),r.get('h')) for r in ok).most_common(12)}")
    lines.append(f"有 EXIF 拍摄时间: {sum(1 for r in ok if r.get('dt'))}")
    lines.append(f"相机: {Counter(r.get('camera') for r in ok).most_common(12)}")
    lines.append("")
    lines.append("=== 按 EXIF 月份 ===")
    for k, v in sorted(Counter(r.get("month", "unknown") for r in ok).items()):
        lines.append(f"  {k}: {v}")
    lines.append("")
    lines.append("=== 按一级目录 ===")
    for k, v in Counter(r.get("section", "?") for r in ok).most_common():
        lines.append(f"  {k}: {v}")
    lines.append("")
    lines.append("=== 按文件夹 (前 80) ===")
    for k, v in Counter(r.get("folder", "?") for r in ok).most_common(80):
        lines.append(f"  {v:5d}  {k}")
    lines.append("")
    lines.append(f"失败样本: {[r['p'] for r in bad[:10]]}")
    txt = "\n".join(lines)
    with open(os.path.join(CACHE, "report.txt"), "w", encoding="utf-8") as f:
        f.write(txt)
    print(txt, flush=True)
    print(f"DONE in {round(time.time()-t0,1)}s", flush=True)


if __name__ == "__main__":
    main()
