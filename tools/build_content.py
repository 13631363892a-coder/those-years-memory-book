# -*- coding: utf-8 -*-
"""按真实 EXIF 拍摄时间重新编排整本相册，生成 assets/js/content.js。

原则：
  1. 只使用「能读到 EXIF 相机信息 + 拍摄时间」的照片（无相机信息的均为非初中图片）。
  2. 全部照片严格按拍摄时间递增，章节边界也按时间切分，不重叠、不倒序。
  3. 版式按节奏错落交替（跨页大图 / 满版 / 拼贴 / 图文故事 / 双图 / 拍立得 / 短句 / 时间线）。
  4. 所有日期来自 EXIF，可考证；文案只用氛围短句与可考证的时间、场景词，不编造经历。

用法: python tools/build_content.py
"""
import os, json, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, "tools_cache")
OUT = os.path.join(ROOT, "assets", "js", "content.js")

IDX = json.load(open(os.path.join(CACHE, "photo-index.json"), encoding="utf-8"))
BY = {r["id"][:6]: r for r in IDX}
SEL = json.load(open(os.path.join(HERE, "selection.json"), encoding="utf-8"))
POOL = sorted({x for k, v in SEL.items() if not k.startswith("_") for x in v})
USED_BEFORE = set(json.load(open(os.path.join(HERE, "used_before.json"), encoding="utf-8")))

# 无相机信息 / 无 EXIF 日期的一律剔除
VALID = [x for x in POOL if (BY[x].get("camera") or "").strip() and BY[x].get("dt")]
INVALID = [x for x in POOL if x not in VALID]

# 上一版已人工精选的照片优先保留；再补入若干经联系表确认过的有效备选，
# 用来填补 2025-12 / 2026-01 / 2026-03 / 毕业傍晚等稀疏时段。
EXTRA = [
    "3382c2", "effa8d", "24560f", "6be79d", "23ed0e", "92c700",  # 2026-01 期末
    "46175a",                                                    # 2026-03 百日誓师
    "4f8cab", "6223ba",                                          # 2026-04 研学
    "0a7ee8", "2b5aac",                                          # 2026-07 校园空镜
]
KEEP = set(x for x in VALID if x in USED_BEFORE) | set(EXTRA)
TIMELINE = sorted((x for x in VALID if x in KEEP), key=lambda x: BY[x]["dt"])

# ---------------- 章节（严格按时间递增） ----------------
CHAPTERS = [
    dict(id="ch1", no="01", title="初二 · 故事的开始", sub="2024 年 11 月 — 2025 年 7 月", tone="tone-1",
         intro="刚开始的时候，谁都没想过会记得这么久。\n校运会、校庆、研学、期末的教室。\n相机里存下了许多当时没在意的一分钟。"),
    dict(id="ch2", no="02", title="少年日常 · 镜头里的我们", sub="2025 年 9 月 — 10 月", tone="tone-2",
         intro="课间十分钟，桌上摊开的练习册，\n有人忽然凑过来比了个耶。\n没有什么大事发生，只是刚好有人按下了快门。"),
    dict(id="ch3", no="03", title="初三 · 时间开始加速", sub="2025 年 11 月 — 2026 年 1 月", tone="tone-3",
         intro="日子忽然变得很整齐：上课、做题、考试，再上课。\n校运会那天的彩色烟雾，礼堂里翻到一半的书。\n忙是真的，热闹也是真的。"),
    dict(id="ch4", no="04", title="初三下 · 最后一段路", sub="2026 年 3 月 — 4 月", tone="tone-4",
         intro="操场上的 2026，和四月又出一趟门的车窗。\n那阵子大家都在往前赶，\n相机却还是照常拍下一些没什么用的瞬间。"),
    dict(id="ch5", no="05", title="那些重要的人", sub="2026 年 7 月 2 日 · 白天", tone="tone-5",
         intro="照片里的人，我一个名字也没写。\n不是忘了，是怕写错，也怕写少了。\n反正看到这些脸，就会想起那一整间教室。"),
    dict(id="ch6", no="06", title="青春散场 · 毕业与告别", sub="2026 年 7 月 2 日 · 傍晚", tone="tone-1",
         intro="拍完合影，镜头又转向教学楼的窗、走廊和天上的云。\n后来相册里，最多的反而是这些没有人的照片。\n那天没有谁说很多话。"),
    dict(id="ch7", no="07", title="尾声 · 故事没有结束", sub="写给过去的自己", tone="tone-2",
         intro="写到最后一页，还是不知道该怎么收尾。\n那就先合上吧。"),
]
CH_BY_ID = {c["id"]: c for c in CHAPTERS}


def chapter_for(dt):
    if dt < "2025:09:01": return "ch1"
    if dt < "2025:11:01": return "ch2"
    if dt < "2026:02:01": return "ch3"
    if dt < "2026:07:01": return "ch4"
    if dt < "2026:07:02 17:25:00": return "ch5"
    return "ch6"


THEME = {
    "2024:11": ("校运会那几天", "2024.11"),
    "2025:05": ("五月，出了一趟门", "2025.05.30"),
    "2025:07": ("学期最后几天", "2025.07"),
    "2025:09": ("九月，开学", "2025.09"),
    "2025:10": ("教室里的日常", "2025.10"),
    "2025:11": ("校运会", "2025.11"),
    "2025:12": ("十二月", "2025.12"),
    "2026:01": ("学期末", "2026.01"),
    "2026:03": ("三月，操场", "2026.03"),
    "2026:04": ("四月，又出了一趟门", "2026.04"),
    "2026:07": ("七月二日", "2026.07.02"),
}
CAPS = ["都还在。", "一整个下午。", "快门按下去的时候，什么也没想。",
        "后来常常想起的，是这种没什么事的时候。", "镜头里的位置，总是刚好。",
        "照片会旧，那天不会。", "那时还不知道要记住什么。", "再看一眼。"]
NOTES = ["有些日子，当时只道是寻常。", "走廊很长，课间很短。", "书还摊着，人已经走开了。",
         "风从走廊那头过来，和两年前一样。", "时间在这里慢了一下。", "后来再没有那样的一整个下午。"]
HEADS = ["没什么事发生的下午", "镜头忽然转过来", "课间十分钟", "按时间排下来",
         "这些都没排练过", "一天里最普通的几分钟", "当时没在意的一分钟", "照片之间的空档"]
STORY_TEXT = [
    "照片是按时间排的，记忆不是。\n能留下来的，多半是些没头没尾的片段。",
    "没有人特意站好，也没有人数够人数。\n快门响了，这一分钟就留下来了。",
    "那年觉得日子过得很慢。\n现在一页一页翻过去，才发现只有薄薄一叠。",
    "教室、走廊、操场，来来回回就这几个地方。\n偏偏怎么也看不腻。",
    "拍得歪的、虚的、手挡住镜头的，都留着。\n当时只觉得普通，后来才知道，那就是那两年。",
]
SHORT_CAPS = ["两个人", "合影", "课间", "回头", "比个耶", "并排", "看镜头", "一抬头",
              "窗边", "课桌前", "操场", "走廊", "笑一个", "低头"]

counters = {"cap": 0, "note": 0, "head": 0, "story": 0, "short": 0}
def pick(key):
    pool = {"cap": CAPS, "note": NOTES, "head": HEADS, "story": STORY_TEXT, "short": SHORT_CAPS}[key]
    v = pool[counters[key] % len(pool)]
    counters[key] += 1
    return v


def theme(ids):
    dt = BY[ids[0]]["dt"]
    return THEME.get(dt[:7], ("那些年", dt[:7].replace(":", ".")))


def real_date(x):
    return BY[x]["dt"][:10].replace(":", ".")


# ---------------- 版式节奏 ----------------
RHYTHM = [("spread", 1), ("story", 2), ("full", 1), ("collage", 5),
          ("duo", 2), ("note", 1), ("story", 2), ("timeline", 3),
          ("frame", 1), ("collage", 4), ("duo", 2), ("full", 1), ("note", 1)]


def make_spec(typ, ids):
    # 尾段照片不足时自动降级，保证每种版式都有合适的照片数量
    if len(ids) < 2 and typ in ("story", "duo", "timeline", "collage"):
        typ = "frame"
    elif typ == "collage" and len(ids) < 3:
        typ = "duo" if len(ids) == 2 else "frame"
    elif typ == "timeline" and len(ids) < 3:
        typ = "duo" if len(ids) == 2 else "frame"
    title, period = theme(ids)
    if typ == "spread":
        return dict(t="spread", photo=ids[0], noteL=title, noteR=period)
    if typ == "full":
        return dict(t="full", photo=ids[0], cap=pick("cap"))
    if typ == "collage":
        ph = [dict(id=x, cap=pick("short") if i % 2 == 0 else "") for i, x in enumerate(ids)]
        return dict(t="collage", title=title, sub=period + " · 照片按拍摄时间排列", photos=ph)
    if typ == "story":
        return dict(t="story", kicker=period, head=pick("head"), text=pick("story"),
                    photos=[dict(id=ids[0], cap=""), dict(id=ids[-1], cap=pick("short") if len(ids) > 1 else "")],
                    foot=real_date(ids[0]) + " — " + real_date(ids[-1]))
    if typ == "duo":
        return dict(t="duo", orient="horizontal" if counters["head"] % 2 else "vertical",
                    head=title, photos=[dict(id=x, cap=pick("short")) for x in ids], foot=period)
    if typ == "frame":
        return dict(t="frame", photo=ids[0], top=title, written=pick("short"),
                    quote=pick("note"), meta=real_date(ids[0]),
                    rotate=[-1.8, 1.5, -1.1, 2.0][counters["cap"] % 4])
    if typ == "note":
        return dict(t="note", photo=ids[0], text=pick("note"), meta=real_date(ids[0]))
    if typ == "timeline":
        items = [dict(id=x, date="auto", text=pick("short")) for x in ids]
        return dict(t="timeline", head=title, sub="日期来自照片本身", items=items)
    raise ValueError(typ)


def main():
    print(f"有效照片 {len(VALID)}，已排除无相机信息 {len(INVALID)} 张: {sorted(INVALID)}")
    print(f"入选时间线 {len(TIMELINE)} 张，{BY[TIMELINE[0]]['dt']} → {BY[TIMELINE[-1]]['dt']}")

    pages = [
        dict(t="cover", photo="2208a8", photoCap="校园 · 2026.07.02"),
        dict(t="endpaper", text="谨以此册，留住那两年"),
        dict(t="title", text="一段不会重来的青春。\n照片都在，日子也还在。"),
        dict(t="toc", note="按拍摄时间，从初二翻到初三。"),
        dict(t="prologue", label="序 · 写在翻开之前",
             text="照片是按时间排好的，记忆却不是。\n有些画面清楚得像昨天，有些只剩一点光和颜色。\n那些没对准焦的、拍歪了的、手挡住镜头的，都留着。\n当时只觉得普通，后来才知道，那就是那两年。",
             sign="—— 整理这些照片的人"),
    ]
    flat_len = len(pages)          # 模拟 normalize 后的页数
    cursor = 0
    current_ch = None
    ri = 0
    chapter_pages = {}
    assigned = []                  # 正文按时间线依次分配的照片，用于顺序校验

    while cursor < len(TIMELINE):
        typ, want = RHYTHM[ri % len(RHYTHM)]
        ri += 1
        # 跨页大图若需要对齐页，则多取一张供对齐用的短句页
        need = (2 if flat_len % 2 == 0 else 1) if typ == "spread" else want
        n = min(need, len(TIMELINE) - cursor)
        batch = TIMELINE[cursor:cursor + n]
        ch = chapter_for(BY[batch[0]]["dt"])
        if ch != current_ch:
            c = CH_BY_ID[ch]
            chapter_pages[ch] = flat_len
            pages.append(dict(t="chapter", id=ch, tone=c["tone"], photo=batch[0]))
            assigned.append(batch[0])
            flat_len += 1
            current_ch = ch
            cursor += 1
            batch = batch[1:]
            if not batch:
                continue

        # 跨页大图的左半必须落在奇数下标；若不在，先用一张照片做图文短句页对齐
        if typ == "spread" and flat_len % 2 == 0:
            one = batch[:1]
            pages.append(make_spec("note", one))
            assigned.extend(one)
            flat_len += 1
            cursor += 1
            batch = batch[1:]
            if not batch:
                continue

        spec = make_spec(typ, batch)
        pages.append(spec)
        assigned.extend(batch)
        flat_len += 2 if spec["t"] == "spread" else 1
        cursor += len(batch)

    # 尾声
    pages += [
        dict(t="chapter", id="ch7", tone="tone-2", photo=TIMELINE[-1]),
        dict(t="quote", text="原来那些平凡的日子，\n后来都成了最想念的日子。"),
        dict(t="letter", head="写给那时候的自己：",
             paras=["你现在大概还觉得，这两年长得望不到头。",
                    "课间的十分钟，走廊尽头的光，放学时总也走不完的那段路，\n都平常得很。",
                    "后来它们被收进一个文件夹里，偶尔点开，\n才发现每一张都舍不得删。",
                    "不用急着长大，也不用特意记住什么。\n该留下的，自己会留下。"],
             sign="—— 翻完这本册子的我"),
        dict(t="endpaperBack", text="故事没有结束"),
        dict(t="backcover", text="故事没有结束"),
    ]
    flat_len += 5
    if flat_len % 2 == 1:
        pages.insert(len(pages) - 1, dict(t="note", photo=TIMELINE[-2], text=pick("note"), meta=""))
        flat_len += 1

    album = dict(
        meta=dict(titleLine1="那些年，", titleLine2="我们一起走过",
                  subtitle="初二至初三 · 一段不会重来的青春",
                  years="初二 — 初三", foot="2024 — 2026",
                  coverChapter="致那段回不去的时光"),
        chapters=[dict(id=c["id"], no=c["no"], title=c["title"], sub=c["sub"], intro=c["intro"]) for c in CHAPTERS],
        pages=pages,
    )
    header = ("/* ============================================================\n"
              "   那些年，我们一起走过 — 内容配置（由 tools/build_content.py 生成）\n"
              "   所有照片严格按真实 EXIF 拍摄时间递增排列；\n"
              "   无 EXIF 相机信息的照片一律不收录；日期不编造。\n"
              "   可手工编辑本文件，或改生成器后重新运行。\n"
              "   ============================================================ */\n")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(header + "window.ALBUM = " + json.dumps(album, ensure_ascii=False, indent=2) + ";\n")

    # 时间顺序校验（封面是引子，不计入时间线）
    bad, last = [], ""
    for x in assigned:
        dt = BY[x]["dt"]
        if dt < last:
            bad.append((x, dt, last))
        last = dt
    all_refs = re.findall(r'"[0-9a-f]{6}"', json.dumps(pages, ensure_ascii=False))
    print(f"页面项 {len(pages)}，展开后约 {flat_len} 页，引用照片 {len(all_refs)} 处 / 去重 {len(set(all_refs))} 张")
    print("章节起始下标:", chapter_pages)
    print("时间倒序处:", len(bad), bad[:5])
    print("已写出:", OUT)


if __name__ == "__main__":
    main()
