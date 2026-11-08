# -*- coding: utf-8 -*-
"""按章节主题筛选候选照片：去连拍重复、按人物/清晰度/分辨率评分，输出精选联系表。
只读 tools_cache，不改动原始照片。
"""
import os, sys, json, math
from collections import defaultdict
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
CACHE = os.path.join(ROOT, "tools_cache")
from make_sheets import make_sheet, SHEETS

RECS = json.load(open(os.path.join(CACHE, "photo-index.json"), encoding="utf-8"))
PEOPLE = json.load(open(os.path.join(CACHE, "people.json"), encoding="utf-8"))

# 主题查询：名称 -> (过滤谓词, 需要的张数)
QUERIES = [
    ("A_初二上_校运会校庆", lambda r: ("校运会+89周年校庆" in r["folder"]) or r.get("month") == "2024-11", 84),
    ("B_初二下_研学",       lambda r: "八年级研学" in r["folder"] or r.get("month") == "2025-05", 84),
    ("C_初二下_学期末",     lambda r: "八年级下学期末" in r["folder"], 42),
    ("D_初二_寒假日常",     lambda r: r["section"] == "卡备份" and r.get("month") in ("2025-01", "2025-02", "2025-03", "2025-04"), 84),
    ("E_初三上_教室日常",   lambda r: "九年级/日常" in r["folder"], 126),
    ("F_初三_校运会",       lambda r: "九年级校运会" in r["folder"], 84),
    ("G_初三_研学誓师",     lambda r: ("九年级研学" in r["folder"]) or ("百日誓师" in r["folder"]) or r.get("month") in ("2026-03", "2026-04"), 84),
    ("H_初三_期末与冬日",   lambda r: r.get("month") in ("2025-12", "2026-01", "2026-02") and r["section"] == "九年级", 84),
    ("I_毕业_最后一天",     lambda r: r["section"] == "初中毕业" or r.get("month") == "2026-07", 126),
    ("J_人物合影_全库",     lambda r: True, 126),
]


def ham(a, b):
    return (int(a, 2) ^ int(b, 2)).bit_count()


def score(r):
    p = PEOPLE.get(r["id"], {})
    person = p.get("person", 0)
    dark = p.get("dark", 0)
    px = (r.get("w", 0) or 0) * (r.get("h", 0) or 0)
    sharp = r.get("sharp", 0) or 0
    s = person * 1.15
    s += min(sharp / 240.0, 1.0) * 2.4
    s += 1.6 if px >= 1_000_000 else (0.4 if px >= 200_000 else -3.2)
    s -= min(dark, 0.8) * 5.0
    s += 0.4 if r.get("dt") else 0
    # 过曝/欠曝
    b = r.get("bright", 128)
    if b < 36 or b > 224:
        s -= 2.0
    return round(s, 2)


def dedup(items, threshold=7, max_per_day=80):
    """按分数降序贪心去重：dHash 相近视为连拍，只留最清晰的一张。"""
    kept, day_count = [], defaultdict(int)
    for r in items:
        d = (r.get("dt") or "")[:10]
        if day_count[d] >= max_per_day:
            continue
        h = r.get("dhash")
        if h:
            dup = False
            for k in kept[-120:]:
                if k.get("dhash") and ham(h, k["dhash"]) <= threshold:
                    dup = True
                    break
            if dup:
                continue
        kept.append(r)
        day_count[d] += 1
    return kept


def main():
    outdir = os.path.join(SHEETS, "curated")
    os.makedirs(outdir, exist_ok=True)
    all_manifest = {}
    all_candidates = {}
    for name, pred, want in QUERIES:
        pool = [r for r in RECS if r.get("ok") and os.path.exists(os.path.join(CACHE, "thumbs", r["id"] + ".jpg")) and pred(r)]
        print(f"{name}: pool={len(pool)}", flush=True)
        ranked = sorted(pool, key=lambda r: -score(r))
        picked = dedup(ranked)[:want]
        for r in picked:
            r["_score"] = score(r)
        all_candidates[name] = [{"id": r["id"], "short": r["id"][:6], "p": r["p"],
                                 "dt": r.get("dt"), "folder": r.get("folder"), "score": r["_score"]}
                                for r in picked]
        n = 0
        for i in range(0, len(picked), 42):
            n += 1
            chunk = picked[i:i + 42]
            fn = f"{name}_{n:02d}.jpg"
            label = f"{name}  {n}/{(len(picked)+41)//42}  ·  精选 {len(picked)} 张 / 池 {len(pool)}"
            man = make_sheet(chunk, label, os.path.join(outdir, fn))
            for m, r in zip(man, chunk):
                m["score"] = r["_score"]
                m["dt"] = r.get("dt")
                m["folder"] = r.get("folder")
            all_manifest[fn] = {"title": label, "items": man}
            print(f"   -> {fn} ({len(chunk)})", flush=True)
    with open(os.path.join(outdir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(all_manifest, f, ensure_ascii=False, indent=1)
    with open(os.path.join(CACHE, "curated.json"), "w", encoding="utf-8") as f:
        json.dump(all_candidates, f, ensure_ascii=False, indent=1)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
