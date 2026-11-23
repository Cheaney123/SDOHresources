"""Builds SDOH_Resources.xlsx from data/resources.json, the single source of truth.

The workbook is regenerated automatically whenever the data changes (see .github/workflows/build.yml),
so the spreadsheet and the web app always match. Edit the data, not the spreadsheet.
"""
import json, datetime
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "data/resources.json").read_text())
OUT = ROOT / "SDOH_Resources.xlsx"

TEAL, DUSK = "008080", "1F3433"
BANDS = ["D4E8F2", "FFFFFF"]          # light blue / white, alternating by county
F = "Arial"
thin = Side(style="thin", color="D3DEDE")
head_fill = PatternFill("solid", fgColor=TEAL)
head_font = Font(name=F, bold=True, color="FFFFFF", size=11)
body_font = Font(name=F, size=10, color=DUSK)
wrap = Alignment(wrap_text=True, vertical="top")

def date(s):
    try:
        return datetime.date.fromisoformat((s or "").strip("'"))
    except ValueError:
        return s or None

def sheet(ws, cols, rows, band_key=None):
    ws.append([c for c, _, _ in cols])
    for i, (_, _, w) in enumerate(cols, 1):
        c = ws.cell(row=1, column=i)
        c.fill, c.font = head_fill, head_font
        c.alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 30
    band, last = 0, None
    for r in rows:
        ws.append([get(r) for _, get, _ in cols])
        n = ws.max_row
        if band_key:
            k = band_key(r)
            if k != last and last is not None:
                band ^= 1
            last = k
        fill = PatternFill("solid", fgColor=BANDS[band])
        for i, (name, _, _) in enumerate(cols, 1):
            c = ws.cell(row=n, column=i)
            c.font, c.alignment, c.border = body_font, wrap, Border(bottom=thin)
            c.fill = fill
            if isinstance(c.value, datetime.date):
                c.number_format = "yyyy-mm-dd"
                c.alignment = Alignment(horizontal="center", vertical="top")
            if name.startswith("Medi-Cal") and str(c.value).startswith("Yes"):
                c.font = Font(name=F, size=10, bold=True, color=DUSK)
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions

import re as _re
links = lambda r: "\n".join(_re.sub(r"^\[([^\]]+)\]\((\S+)\)$", r"\1: \2", l) for l in (r.get("links") or []))
COUNTY = [("County", lambda r: r["county"], 13), ("Identified need", lambda r: r["need"], 20),
          ("Resource / agency", lambda r: r["label"], 36), ("Phone", lambda r: r["phone"], 22),
          ("Medi-Cal required", lambda r: r["medi"], 13), ("Who it's for", lambda r: r.get("who"), 30),
          ("How to refer", lambda r: r.get("how"), 44), ("Website", lambda r: r.get("web"), 28),
          ("Notes", lambda r: r.get("notes"), 34), ("Patient summary (plain language)", lambda r: r["summary"], 48),
          ("Links / PDFs to send", links, 48), ("Suggested Z-code(s)", lambda r: r.get("zcodes"), 34),
          ("Last updated", lambda r: date(r.get("updated")), 13), ("Source", lambda r: r.get("source"), 30),
          ("Flag", lambda r: r.get("flag"), 30)]
STATE = [("Identified need", lambda r: r["need"], 20), ("Resource", lambda r: r["label"], 36),
         ("Phone", lambda r: r["phone"], 22), ("Medi-Cal required", lambda r: r["medi"], 13),
         ("Who it's for", lambda r: r.get("who"), 30), ("How to use", lambda r: r.get("how"), 44),
         ("Patient summary (plain language)", lambda r: r["summary"], 48), ("Links / PDFs to send", links, 48),
         ("Suggested Z-code(s)", lambda r: r.get("zcodes"), 34), ("Last updated", lambda r: date(r.get("updated")), 13),
         ("Source", lambda r: r.get("source"), 30), ("Flag", lambda r: r.get("flag"), 30)]

wb = Workbook()
info = wb.active; info.title = "Read me"
county_rows = sorted(D["county"], key=lambda r: (r["county"], int(r["id"][1:])))
lines = [("SDOH Resources by County", Font(name=F, bold=True, size=16, color=TEAL)),
         (f"Generated automatically from the web app's data on {datetime.date.today():%B %-d, %Y}. "
          f"{len(D['county'])} county resources in {len({r['county'] for r in D['county']})} counties, "
          f"{len(D['state'])} statewide resources.", body_font),
         ("This file is rebuilt every time the resource data changes, so it always matches the web app. "
          "Edits made in this file are not carried back: send corrections to the social worker.", body_font),
         ("Links are checked automatically every week; results are posted as an issue in the GitHub repository.", body_font),
         ("Suggested Z-codes are ICD-10-CM FY2027 suggestions only. The clinician assigns codes from the documented assessment.", body_font),
         ("Internal resource guide. No PHI.", Font(name=F, bold=True, size=10, color=DUSK))]
for i, (t, f) in enumerate(lines, 1):
    c = info.cell(row=i * 2 - 1, column=1, value=t); c.font = f; c.alignment = Alignment(wrap_text=True, vertical="top")
info.column_dimensions["A"].width = 110
sheet(wb.create_sheet("County Resources"), COUNTY, county_rows, band_key=lambda r: r["county"])
sheet(wb.create_sheet("Statewide"), STATE, D["state"], band_key=lambda r: r["need"])
wb.save(OUT)
print(f"Wrote {OUT.name}: {len(county_rows)} county + {len(D['state'])} statewide rows")
