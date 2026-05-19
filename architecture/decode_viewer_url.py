#!/usr/bin/env python3
"""Decode draw.io #R fragment from viewer URL."""
import sys
import urllib.parse
import zlib
import base64
import re

def decode_r(data: str) -> str:
    data = data.strip()
    if data.startswith("R"):
        data = data[1:]
    # URL decode
    xml = urllib.parse.unquote(data)
    if xml.startswith("<mxfile"):
        return xml
    # try base64 + deflate (draw.io compressed format)
    try:
        raw = base64.b64decode(data)
        return zlib.decompress(raw, -zlib.MAX_WBITS).decode("utf-8")
    except Exception:
        pass
    try:
        return zlib.decompress(base64.urlsafe_b64decode(data + "==")).decode("utf-8")
    except Exception:
        pass
    return xml


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/architecture/viewer_fragment.txt"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"#R(.+)$", content, re.DOTALL)
    frag = m.group(1) if m else content
    xml = decode_r(frag)
    out = "/workspace/architecture/decoded_user_diagram.xml"
    with open(out, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"Decoded {len(xml)} chars -> {out}")
    print(xml[:500])
