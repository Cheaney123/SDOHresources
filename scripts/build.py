"""Build index.html from src/template.html and data/resources.json.

The resource list is embedded in the page so it works as a single file
(GitHub Pages, a shared drive, or opened directly in a browser).

Usage:  python3 scripts/build.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
template = (ROOT / "src" / "template.html").read_text(encoding="utf-8")
data = json.loads((ROOT / "data" / "resources.json").read_text(encoding="utf-8"))

# Basic checks before building
ids = [r["id"] for r in data["county"] + data["state"]]
assert len(ids) == len(set(ids)), "Duplicate resource ids in data/resources.json"
for r in data["county"] + data["state"]:
    assert r.get("name"), f"{r['id']} has no name"
    assert r.get("summary"), f"{r['id']} has no patient summary"
    assert "{phone}" not in r["summary"], f"{r['id']} summary still has {{phone}}"
    for link in r.get("links") or []:
        assert "https://" in link, f"{r['id']} link is not https: {link}"

embedded = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
html = template.replace("__DATA__", embedded)
(ROOT / "index.html").write_text(html, encoding="utf-8")
print(f"Built index.html: {len(data['county'])} county and {len(data['state'])} statewide resources")
