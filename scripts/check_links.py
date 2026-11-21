"""Link checker for data/services.json. Run where outbound web access is allowed (e.g. a scheduled GitHub Action).

It only REPORTS: broken links, redirects and pages whose text no longer contains a recorded claim's key number.
It never marks anything verified; a person reviews each item and updates review.status / review.date.
Output: link-report.json (add to a draft pull request or review queue).

Usage: python3 scripts/check_links.py [--limit N]
"""
import json, re, sys, urllib.request, urllib.error, ssl, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "data/services.json").read_text())
limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
ctx = ssl.create_default_context()
UA = {"User-Agent": "ResourceReferralPrototype-linkcheck/2.0 (staff directory maintenance)"}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            body = r.read(400_000).decode("utf-8", "ignore")
            return {"status": r.status, "final": r.geturl(), "body": body}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "final": url, "body": ""}
    except Exception as e:  # DNS, timeout, blocked
        return {"status": None, "final": url, "body": "", "error": type(e).__name__}

items, seen = [], {}
urls = []
for s in D["services"]:
    for L in s.get("links", []):
        urls.append((s["id"], "link", L["url"], None))
    for c in s.get("review", {}).get("claims", []):
        nums = re.findall(r"\d{3}\D{0,2}\d{3}-\d{4}", c["claim"])
        urls.append((s["id"], "claim", c["url"], [re.sub(r"\D", "", n) for n in nums]))
if limit:
    urls = urls[:limit]
for sid, kind, url, nums in urls:
    r = seen.get(url) or fetch(url)
    seen[url] = r
    issue = None
    if r["status"] is None:
        issue = "unreachable (" + r.get("error", "") + ")"
    elif r["status"] >= 400:
        issue = f"HTTP {r['status']}"
    elif r["final"].rstrip("/") != url.rstrip("/"):
        issue = f"redirects to {r['final']}"
    if kind == "claim" and nums and r["body"]:
        page = re.sub(r"\D", "", r["body"])
        missing = [n for n in nums if n not in page]
        if missing:
            issue = (issue + "; " if issue else "") + "claim number not found on page: " + ", ".join(missing)
    if issue:
        items.append({"id": sid, "kind": kind, "url": url, "issue": issue, "action": "Review by a person; do not auto-verify."})

out = {"generated": datetime.date.today().isoformat(), "checked": len(seen), "items": items}
(ROOT / "link-report.json").write_text(json.dumps(out, indent=1))
print(f"checked {len(seen)} URLs; {len(items)} items need review -> link-report.json")
