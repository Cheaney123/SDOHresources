"""Weekly link check for data/resources.json.

Opens every link and website once, follows redirects, and sorts each into:
  BROKEN   - 404/410/5xx, DNS or connection failure, or a page whose title says "not found"/error
  MOVED    - works, but sends people to a different website (update the link when convenient;
             redirects within the same site, like short links, count as OK)
  MANUAL   - the site blocks automated checks (403/429/bot challenge) or has a certificate problem; open it by hand
  OK       - loads normally

Writes link-report.md (for the GitHub issue) and link-report.json. Exit code is always 0; the workflow
decides what to do from the counts. Nothing in the data is changed: every fix goes through review.
"""
import json, re, sys, time, concurrent.futures as cf
from pathlib import Path
from urllib.parse import urlparse
import requests

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "data/resources.json").read_text())
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
HEAD = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"}
NOT_FOUND = re.compile(r"\b(404|not found|page (?:cannot|can't|could not) be found|page not available|error)\b", re.I)
BOT = re.compile(r"(just a moment|attention required|access denied|captcha|verify you are human|cloudflare)", re.I)

def urls_of(r):
    found = []
    for l in r.get("links") or []:
        found += re.findall(r"https?://[^\s|]+", l)
    w = (r.get("web") or "").strip()
    if w and w not in ("—", "-") and "." in w and " " not in w.split(";")[0]:
        for part in re.split(r"\s*[;/]\s+|\s+/\s+", w):
            part = part.strip()
            if part and "." in part and " " not in part:
                found.append(part if part.startswith("http") else "https://" + part)
    return [u.rstrip(".,)") for u in found]

def norm(u):
    p = urlparse(u)
    return (p.netloc.lower().removeprefix("www."), p.path.rstrip("/").lower())

def check(url):
    for attempt in range(2):
        try:
            r = requests.get(url, headers=HEAD, timeout=25, allow_redirects=True, stream=True)
            body = b""
            ctype = r.headers.get("content-type", "")
            if "html" in ctype:
                for chunk in r.iter_content(4096):
                    body += chunk
                    if len(body) > 200_000:
                        break
            r.close()
            text = body.decode("utf-8", "ignore")
            m = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
            title = re.sub(r"\s+", " ", m.group(1)).strip()[:140] if m else ""
            final = r.url
            st = r.status_code
            if st in (401, 403, 429, 503) and (BOT.search(text) or st in (403, 429)):
                return dict(status="MANUAL", code=st, final=final, title=title, why="site blocks automated checks")
            if st >= 400:
                return dict(status="BROKEN", code=st, final=final, title=title, why=f"HTTP {st}")
            if title and NOT_FOUND.search(title) and not re.search(r"error-?free", title, re.I):
                return dict(status="BROKEN", code=st, final=final, title=title, why="page title says not found/error")
            same_site = norm(final)[0] == norm(url)[0]
            is_file = re.search(r"\.(pdf|docx?|xlsx?)$", urlparse(final).path, re.I)
            if norm(final) != norm(url) and not same_site and not is_file:
                return dict(status="MOVED", code=st, final=final, title=title, why="redirects to another website")
            return dict(status="OK", code=st, final=final, title=title, why="")
        except requests.exceptions.SSLError:
            return dict(status="MANUAL", code=None, final=url, title="", why="security certificate problem")
        except Exception as e:
            err = type(e).__name__
            if attempt == 0:
                time.sleep(3); continue
            if re.search(r"NameResolution|getaddrinfo|Name or service not known|nodename nor servname", str(e)):
                return dict(status="BROKEN", code=None, final=url, title="", why="website address no longer exists")
            # Some small sites refuse connections from cloud servers but open normally in a browser
            return dict(status="MANUAL", code=None, final=url, title="", why="site refused the automated connection")

def main():
    uses = {}
    for r in D["county"] + D["state"]:
        for u in urls_of(r):
            uses.setdefault(u, []).append(r)
    with cf.ThreadPoolExecutor(12) as ex:
        res = dict(zip(uses, ex.map(check, uses)))
    conf_path = ROOT / "data/links_confirmed.json"
    confirmed = json.loads(conf_path.read_text()) if conf_path.exists() else {}
    import datetime as dt
    for u, v in res.items():
        d = confirmed.get(u)
        if v["status"] == "MANUAL" and d and (dt.date.today() - dt.date.fromisoformat(d)).days <= 120:
            v["status"], v["why"] = "CONFIRMED", f"blocks automated checks; confirmed by hand {d}"
    order = {"BROKEN": 0, "MANUAL": 1, "MOVED": 2, "CONFIRMED": 3, "OK": 4}
    counts = {k: sum(v["status"] == k for v in res.values()) for k in order}
    rows = []
    for u, v in sorted(res.items(), key=lambda kv: (order[kv[1]["status"]], kv[0])):
        who = uses[u]
        names = sorted({(r.get("county") or "Statewide") + ": " + r["name"] for r in who})
        rows.append({"url": u, **v, "uses": len(who), "resources": names, "ids": sorted({r["id"] for r in who})})
    today = time.strftime("%Y-%m-%d")
    json.dump({"date": today, "counts": counts, "links": rows}, open(ROOT / "link-report.json", "w"), indent=1)
    md = [f"Weekly link check, {today}: **{len(res)}** links checked.",
          f"Broken: **{counts['BROKEN']}** · Check by hand: **{counts['MANUAL']}** · Moved: **{counts['MOVED']}** · "
          f"Confirmed by hand earlier: {counts['CONFIRMED']} · OK: {counts['OK']}", ""]
    labels = {"BROKEN": "Broken: fix or replace", "MANUAL": "Check by hand (site blocks automated checks)",
              "MOVED": "Moved: still works, update the address when convenient",
              "CONFIRMED": "No action: blocks automated checks, but confirmed by hand in the last 120 days"}
    for k in ("BROKEN", "MANUAL", "MOVED", "CONFIRMED"):
        sel = [x for x in rows if x["status"] == k]
        if not sel:
            continue
        md += [f"### {labels[k]} ({len(sel)})", "", "| Link | Result | Used by |", "| --- | --- | --- |"]
        for x in sel:
            res_txt = x["why"] + (f" → {x['final']}" if k == "MOVED" else "")
            used = "; ".join(x["resources"][:3]) + (f" (+{len(x['resources']) - 3} more)" if len(x["resources"]) > 3 else "")
            md.append(f"| {x['url']} | {res_txt} | {used} |")
        md.append("")
    md.append("After opening a 'check by hand' link and finding it correct, add it with today's date to `data/links_confirmed.json` (or ask Claude).")
    md.append("")
    md.append("Nothing was changed automatically. Fix links in `data/resources.json` (or ask Claude), and the app and spreadsheet update together.")
    (ROOT / "link-report.md").write_text("\n".join(md))
    print("\n".join(md[:2]))

if __name__ == "__main__":
    main()
