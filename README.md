# Sync Resource Referral

An internal web app for the **Sutter Sync Heart Health Program** care team. Staff select a patient's county, identified need and Medi-Cal status, tick the resources discussed on the call, and copy a finished, patient-friendly message into My Health Online (MHO).

> **Do not enter PHI in this web app.** It stores nothing about patients. The only thing saved in the browser is the last county selected.

## What it does

- **Patient details:** County (23 Sutter counties), Identified need, and Medi-Cal (Yes / No / Unsure).
  - **No** hides Medi-Cal-only resources.
  - **Unsure** shows them with a "confirm coverage" tag.
- **Resources:** county resources plus statewide lines. Each card shows the phone number, need, Medi-Cal tag, and a Details panel (who it's for, how to refer, notes, links, source). A yellow dot marks a detail that isn't fully verified.
- **MHO message:** builds as resources are ticked. Resource names and phone numbers are bold, links are labeled, and the wording adjusts for one or several resources. Staff can reorder, remove, or edit before copying.
- **Safety first** bar: 911, 988 with MD notification per Sync escalation, and APS 833-401-0832 with mandated-report steps.

## Files

| Path | Purpose |
|---|---|
| `index.html` | The built app: one self-contained file, ready to host or open |
| `src/template.html` | Page layout, styles and logic (edit this, not `index.html`) |
| `data/resources.json` | All county and statewide resources, patient summaries, links and message closing |
| `scripts/build.py` | Puts the data into the template and writes `index.html` (with basic data checks) |
| `tests/test_all_scenarios.py` | Runs all 864 County × Need × Medi-Cal combinations in a browser |

## Updating resources

1. Edit `data/resources.json`. The fields for each resource are:
   - `name`: the name patients see
   - `phone`
   - `summary`: the plain-language patient text, which must include the phone number
   - `links`: written as `Label: https://...`
   - `medi`, `who`, `how`, `notes`, `source`, `verified`: shown to staff
   - `flag`: shows the yellow dot
2. Rebuild: `python3 scripts/build.py`
3. Test: `python3 tests/test_all_scenarios.py`
4. Commit and push.

The master list lives in the Sync SDOH resource spreadsheet. Keep the two in step when numbers change.

## Running locally

Open `index.html` in a browser. Nothing to install.

## Publishing with GitHub Pages

1. Push this folder to a GitHub repository.
2. Go to **Settings → Pages**, set **Source** to *Deploy from a branch*, choose `main` and `/ (root)`, then save.
3. The app is served at `https://<your-account>.github.io/<repo-name>/`.

Keep the repository **private** unless Sutter has approved making it public. It describes internal Sync workflows and escalation steps. Pages on private repositories needs a paid GitHub plan; Sutter IT may prefer to host it internally.

## Testing

```bash
pip install playwright
python -m playwright install chromium
python3 scripts/build.py
python3 tests/test_all_scenarios.py
```

The test fails on any mismatch, for example:
- a resource listed under the wrong county or need
- a Medi-Cal-only resource shown when Medi-Cal is "No"
- 911 missing
- a message with a leftover placeholder or non-https link
- a phone number missing from the patient text

## Known gaps (Nov 2026)

- **Housing & legal:** local listings exist only for Sacramento, San Francisco, San Mateo and Santa Clara. Other counties show the statewide Senior Legal Hotline and 211.
- **Statewide only:** Insurance & benefits, Medication costs, Phone access and Safety / crisis have statewide resources only.
- **Not yet verified:** details marked with a yellow dot, and whether bold formatting survives pasting into MHO.

## Brand

Sutter colors: Teal `#008080`, Dusky Teal `#1F3433`, Yellow `#EFC469`, Breezy Teal `#01EFE1` (dark mode accent). Fonts: Sora for headings, Roboto for body text, from Google Fonts.
