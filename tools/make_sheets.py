# -*- coding: utf-8 -*-
"""生成照片联系表(contact sheet)，用于人工挑选。不修改原始照片。
用法:
  python make_sheets.py --mode sample --per 24 --out overview
  python make_sheets.py --mode full --group 八年级 --out grade8
  python make_sheets.py --mode full --month 2026-07 --out grad
"""
import os, sys, json, argparse, math
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "tools_cache")
THUMBS = os.path.join(CACHE, "thumbs")
SHEETS = os.path.join(CACHE, "sheets")

FONT_PATHS = [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf",
              r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\arial.ttf"]


def font(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def short_label(rec):
    return rec["id"][:6]


def make_sheet(records, title, outpath, cols=7, rows=6, cell_w=176, cell_h=150):
    per = cols * rows
    pad = 16
    header = 42
    W = pad * 2 + cols * cell_w
    H = pad * 2 + header + rows * cell_h
    sheet = Image.new("RGB", (W, H), (242, 238, 228))
    d = ImageDraw.Draw(sheet)
    f_title = font(19)
    f_lbl = font(12)
    d.text((pad, 10), title, fill=(72, 60, 46), font=f_title)
    manifest = []
    for idx, rec in enumerate(records[:per]):
        r, c = divmod(idx, cols)
        x = pad + c * cell_w
        y = pad + header + r * cell_h
        d.rectangle([x, y, x + cell_w - 6, y + cell_h - 6], fill=(255, 253, 247),
                    outline=(203, 194, 176), width=1)
        tp = os.path.join(THUMBS, rec["id"] + ".jpg")
        if os.path.exists(tp):
            try:
                im = Image.open(tp).convert("RGB")
                im.thumbnail((cell_w - 12, cell_h - 34), Image.Resampling.LANCZOS)
                ix = x + (cell_w - 6 - im.width) // 2
                iy = y + 2 + (cell_h - 32 - im.height) // 2
                sheet.paste(im, (ix, iy))
            except Exception:
                pass
        label = short_label(rec)
        dt = (rec.get("dt") or "")[5:10].replace(":", ".")
        txt = f"{label}  {dt}"
        d.text((x + 4, y + cell_h - 27), txt, fill=(86, 72, 56), font=f_lbl)
        manifest.append({"short": label, "id": rec["id"], "p": rec["p"],
                         "dt": rec.get("dt"), "folder": rec.get("folder")})
    sheet.save(outpath, quality=88)
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="sample", choices=["sample", "full"])
    ap.add_argument("--per", type=int, default=24)
    ap.add_argument("--group", default=None, help="一级目录或文件夹子串")
    ap.add_argument("--month", default=None)
    ap.add_argument("--out", default="overview")
    ap.add_argument("--min-sharp", type=float, default=0)
    ap.add_argument("--sort", default="time", choices=["time", "path", "sharp"])
    ap.add_argument("--group-by", default="folder", choices=["folder", "month", "section", "none"])
    ap.add_argument("--ids-from", default=None, help="只输出这些 6 位短码(逗号分隔)")
    args = ap.parse_args()

    recs = json.load(open(os.path.join(CACHE, "photo-index.json"), encoding="utf-8"))
    recs = [r for r in recs if r.get("ok") and os.path.exists(os.path.join(THUMBS, r["id"] + ".jpg"))]
    if args.group:
        recs = [r for r in recs if args.group in r["section"] or args.group in r["folder"]]
    if args.month:
        recs = [r for r in recs if r.get("month") == args.month]
    if args.min_sharp:
        recs = [r for r in recs if r.get("sharp", 0) >= args.min_sharp]
    if args.ids_from:
        wanted = set(x.strip() for x in args.ids_from.split(",") if x.strip())
        recs = [r for r in recs if r["id"][:6] in wanted]
    if args.sort == "time":
        recs.sort(key=lambda r: (r.get("dt") or "9999", r["p"]))
    elif args.sort == "sharp":
        recs.sort(key=lambda r: -r.get("sharp", 0))
    else:
        recs.sort(key=lambda r: r["p"])

    os.makedirs(SHEETS, exist_ok=True)
    outdir = os.path.join(SHEETS, args.out)
    os.makedirs(outdir, exist_ok=True)

    groups = defaultdict(list)
    for r in recs:
        if args.mode == "sample":
            key = {"folder": r["folder"], "month": r.get("month") or "unknown",
                   "section": r["section"], "none": "全部"}[args.group_by]
        else:
            key = {"folder": r["folder"], "month": r.get("month") or "unknown",
                   "section": r["section"], "none": "全部"}[args.group_by]
        groups[key].append(r)

    manifest_all = {}
    n_sheet = 0
    jobs = []
    if args.mode == "sample":
        # 每组均匀抽样，全部合并成连续流后分页，便于快速总览
        stream = []
        for key in sorted(groups):
            items = groups[key]
            k = min(args.per, len(items))
            if k <= 0:
                continue
            if k == len(items):
                picked = items
            else:
                picked = [items[round(i * (len(items) - 1) / (k - 1))] for i in range(k)]
            for p in picked:
                stream.append((key, p))
        chunks = [stream[i:i + 42] for i in range(0, len(stream), 42)]
        for i, chunk in enumerate(chunks):
            jobs.append(([x[1] for x in chunk],
                         f"{args.out} — 抽样总览 {i+1}/{len(chunks)}  (组: {chunk[0][0]} … {chunk[-1][0]})"))
        # 让 manifest 记录每组来源
        for chunk in chunks:
            for key, rec in chunk:
                rec["_sample_group"] = key
    else:
        for key in sorted(groups):
            items = groups[key]
            chunks = [items[i:i + 42] for i in range(0, len(items), 42)]
            for i, chunk in enumerate(chunks):
                jobs.append((chunk, f"{key}  {i+1}/{len(chunks)}  (共 {len(items)})"))

    for chunk, label in jobs:
            n_sheet += 1
            fn = f"{n_sheet:03d}.jpg"
            man = make_sheet(chunk, label, os.path.join(outdir, fn))
            manifest_all[fn] = {"title": label, "items": man}
            print(f"  {fn}  {label}", flush=True)
    with open(os.path.join(outdir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_all, f, ensure_ascii=False, indent=1)
    print(f"DONE {n_sheet} sheets -> {outdir}", flush=True)


if __name__ == "__main__":
    main()
