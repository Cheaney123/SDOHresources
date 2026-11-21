"""Build index.html from src/template.html + data + pilot config.
Usage: python3 scripts/build.py [--data data/services.json] [--pilot config/pilot.json] [--out index.html]
"""
import json, sys, argparse
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--data", default=str(ROOT / "data/services.json"))
ap.add_argument("--pilot", default=str(ROOT / "config/pilot.json"))
ap.add_argument("--out", default=str(ROOT / "index.html"))
a = ap.parse_args()
data = json.loads(Path(a.data).read_text())
pilot = json.loads(Path(a.pilot).read_text())
def emb(o): return json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
t = (ROOT / "src/template.html").read_text()
assert "__DATA__" in t and "__PILOT__" in t
html = t.replace("__DATA__", emb(data)).replace("__PILOT__", emb(pilot))
Path(a.out).write_text(html)
print("built", a.out, len(html) // 1024, "KB,", len(data["services"]), "services")
