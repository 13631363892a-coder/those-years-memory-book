# -*- coding: utf-8 -*-
"""JPEG/PNG 快速元数据 + EXIF 内嵌缩略图提取（只读文件头部，极快）。"""
import io, os, struct
from PIL import Image

EXIF_DT_KEYS = (0x9003, 0x9004, 0x0132)  # DateTimeOriginal, Digitized, DateTime
EXIF_ORIENT = 0x0112
EXIF_MAKE = 0x010F
EXIF_MODEL = 0x0110

TYPESIZE = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8}


def _entries(seg, off, endian):
    if off + 2 > len(seg):
        return {}, 0
    n = struct.unpack_from(endian + "H", seg, off)[0]
    out = {}
    for k in range(n):
        q = off + 2 + k * 12
        if q + 12 > len(seg):
            break
        tag, typ, cnt = struct.unpack_from(endian + "HHI", seg, q)
        size = TYPESIZE.get(typ, 1) * cnt
        if size <= 4:
            val = seg[q + 8:q + 8 + size]
        else:
            o = struct.unpack_from(endian + "I", seg, q + 8)[0]
            val = seg[o:o + size]
        out[tag] = (typ, cnt, val)
    nxt = 0
    p = off + 2 + n * 12
    if p + 4 <= len(seg):
        nxt = struct.unpack_from(endian + "I", seg, p)[0]
    return out, nxt


def _as_int(v, endian):
    if isinstance(v, bytes):
        if len(v) == 2:
            return struct.unpack(endian + "H", v)[0]
        if len(v) == 4:
            return struct.unpack(endian + "I", v)[0]
    return 0


def _as_str(v):
    if isinstance(v, bytes):
        return v.split(b"\x00")[0].decode("ascii", "ignore").strip()
    return ""


def parse_head(path, head_bytes=300000):
    """返回 {w,h,exif_dt,camera,orient,thumb,sofformat}。thumb 为 JPEG 字节或 None。"""
    info = {}
    with open(path, "rb") as f:
        data = f.read(head_bytes)
    info["bytes"] = os.stat(path).st_size
    if data[:2] != b"\xff\xd8":
        # PNG / 其它：交给 Pillow 兜底
        with Image.open(path) as im:
            info["w"], info["h"] = im.size
            info["fmt"] = im.format
            ex = im.getexif()
            dt = ex.get(36867) or ex.get(36868) or ex.get(306)
            if isinstance(dt, bytes):
                dt = dt.decode("ascii", "ignore")
            if isinstance(dt, str) and len(dt) >= 10 and dt[:4].isdigit():
                info["exif_dt"] = dt.strip()[:19]
            info["orient"] = ex.get(274, 1)
            try:
                info["camera"] = (str(ex.get(271, "")) + " " + str(ex.get(272, ""))).strip()
            except Exception:
                pass
        return info
    info["fmt"] = "JPEG"
    i = 2
    while i < len(data) - 4:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        if i + 4 > len(data):
            break
        length = struct.unpack_from(">H", data, i + 2)[0]
        if length < 2:
            break
        seg_end = i + 2 + length
        # SOF: 尺寸
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            if i + 9 <= len(data):
                info["h"] = struct.unpack_from(">H", data, i + 5)[0]
                info["w"] = struct.unpack_from(">H", data, i + 7)[0]
        # APP1: EXIF
        elif marker == 0xE1 and data[i + 4:i + 10] == b"Exif\x00\x00":
            seg = data[i + 10:i + 2 + length]
            if len(seg) >= 8 and seg[:2] in (b"II", b"MM"):
                endian = "<" if seg[:2] == b"II" else ">"
                try:
                    ifd0 = struct.unpack_from(endian + "I", seg, 4)[0]
                    t0, ifd1off = _entries(seg, ifd0, endian)
                    for k in EXIF_DT_KEYS:
                        if k in t0 and not info.get("exif_dt"):
                            s = _as_str(t0[k][2])
                            if len(s) >= 10 and s[:4].isdigit():
                                info["exif_dt"] = s[:19]
                    if EXIF_ORIENT in t0:
                        info["orient"] = _as_int(t0[EXIF_ORIENT][2], endian)
                    mk = _as_str(t0[EXIF_MAKE][2]) if EXIF_MAKE in t0 else ""
                    md = _as_str(t0[EXIF_MODEL][2]) if EXIF_MODEL in t0 else ""
                    if mk or md:
                        info["camera"] = (mk + " " + md).strip()
                    if ifd1off:
                        t1, _ = _entries(seg, ifd1off, endian)
                        if 0x0201 in t1 and 0x0202 in t1:
                            o = _as_int(t1[0x0201][2], endian)
                            ln = _as_int(t1[0x0202][2], endian)
                            if 0 < ln < 200000 and o + ln <= len(seg):
                                b = seg[o:o + ln]
                                if b[:2] == b"\xff\xd8":
                                    info["thumb"] = b
                except Exception:
                    pass
        if seg_end > len(data):
            break
        if info.get("w") and info.get("thumb") is not None:
            break
        i += 2 + length
    return info


def thumb_image(info):
    if info.get("thumb"):
        try:
            return Image.open(io.BytesIO(info["thumb"])).convert("RGB")
        except Exception:
            return None
    return None
