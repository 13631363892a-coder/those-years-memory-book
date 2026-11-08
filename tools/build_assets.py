# -*- coding: utf-8 -*-
"""根据 selection.json 生成相册本地静态图片与照片索引。
  - 原始照片只读，绝不修改/移动/删除
  - thumb: WebP，最长边 1200，用于书页
  - full : JPEG，最长边 2000，仅放大查看时按需加载
用法: python build_assets.py
"""
import os, sys, json, hashlib, time
from PIL import Image, ImageOps, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

ROOT = os.path.dirname(os.path.abspath(__file__))          # album/tools
ALBUM = os.path.dirname(ROOT)                              # album
CACHE = os.path.join(ALBUM, "tools_cache")
SRC_ROOT = r"F:\佳能\初中"
SEL = os.path.join(ROOT, "selection.json")
THUMB_DIR = os.path.join(ALBUM, "photos", "thumb")
FULL_DIR = os.path.join(ALBUM, "photos", "full")


def main():
    if not os.path.exists(SEL):
        print("缺少 selection.json"); sys.exit(1)
    sel = json.load(open(SEL, encoding="utf-8"))
    shorts = []
    if isinstance(sel, dict):
        for k, v in sel.items():
            if isinstance(v, list):
                shorts += v
    else:
        shorts = list(sel)
    shorts = list(dict.fromkeys(shorts))
    print("选片数量:", len(shorts), flush=True)

    recs = json.load(open(os.path.join(CACHE, "photo-index.json"), encoding="utf-8"))
    by_short = {}
    for r in recs:
        s = r["id"][:6]
        if s in by_short:
            print("  ! 短码冲突:", s, by_short[s]["p"], r["p"], flush=True)
        by_short.setdefault(s, r)

    os.makedirs(THUMB_DIR, exist_ok=True)
    os.makedirs(FULL_DIR, exist_ok=True)
    out_index, out_map = {}, {}
    t0 = time.time()
    missing = []
    for i, s in enumerate(shorts, 1):
        r = by_short.get(s)
        if not r:
            missing.append(s); continue
        src = os.path.join(SRC_ROOT, r["p"])
        if not os.path.exists(src):
            missing.append(s); continue
        try:
            with Image.open(src) as im:
                im = ImageOps.exif_transpose(im)
                im = im.convert("RGB")
                w, h = im.size
                # 缩略图
                t = im.copy()
                t.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                t.save(os.path.join(THUMB_DIR, s + ".webp"), "WEBP", quality=82, method=5)
                # 放大图
                f = im.copy()
                f.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
                f.save(os.path.join(FULL_DIR, s + ".jpg"), "JPEG", quality=85, optimize=True)
            out_index[s] = {"dt": r.get("dt") or "", "w": w, "h": h,
                            "ratio": round(w / h, 3) if h else 1}
            out_map[s] = {"src": r["p"], "dt": r.get("dt") or "", "folder": r.get("folder"),
                          "camera": r.get("camera"), "w": w, "h": h}
        except Exception as e:
            print("  ! 处理失败", s, str(e)[:100], flush=True)
            missing.append(s)
        if i % 25 == 0:
            print(f"  {i}/{len(shorts)}  {round(time.time()-t0,1)}s", flush=True)

    with open(os.path.join(ALBUM, "assets", "js", "photo-index.js"), "w", encoding="utf-8") as f:
        f.write("/* 自动生成，请勿手改；由 tools/build_assets.py 生成 */\n")
        f.write("window.PHOTO_INDEX = ")
        json.dump(out_index, f, ensure_ascii=False, indent=1)
        f.write(";\n")
    with open(os.path.join(ROOT, "photo-map.json"), "w", encoding="utf-8") as f:
        json.dump(out_map, f, ensure_ascii=False, indent=1)
    print(f"DONE 生成 {len(out_index)} 张，失败 {len(missing)}，耗时 {round(time.time()-t0,1)}s", flush=True)
    if missing:
        print("未找到:", missing, flush=True)
    # 体积
    for d in (THUMB_DIR, FULL_DIR):
        total = sum(os.path.getsize(os.path.join(d, x)) for x in os.listdir(d))
        print(f"  {d}: {total/1024**2:.1f} MB", flush=True)


if __name__ == "__main__":
    main()
