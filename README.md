# Resource Referral Prototype

Internal staff referral guide. No PHI is collected.

This version brings in the corrections and workflow from the 2.0 pilot build. The earlier directory is kept as read-only input (`data/legacy-v1.json`) and rebuilt into `data/services.json` by `scripts/migrate.py`.

Staff turn a need they heard into:
- **one patient next step**, as a My Health Online message, a read-aloud script, or a printed copy, and
- **a factual staff note** for the chart.

Both are built from the same confirmed facts. Nothing is saved, sent or logged; the page has no backend.

## Preview

Live: https://cheaney123.github.io/SDOHresources/ (and the Cloudflare Workers copy, if it deploys from this repo). Locally, open `index.html`; it is one self-contained file.

## What changed from v1

| Area | Before (baseline, recorded 2026-11-20) | Now |
|---|---|---|
| Retired CalFresh flier PDF | In every food output | Removed everywhere; content check fails the build if it returns |
| CalFresh application | "Apply for CalFresh: getcalfresh.org" | Apply: BenefitsCal. GetCalFresh labelled "information and help applying" |
| Sacramento groceries | Food bank main line | Food Finder link first; CalFresh team 916-779-0052 labelled by purpose |
| Medi-Cal rides | Plan member-services lines shown as "ride lines" | Ride scheduling and member services labelled separately; verified Anthem, Health Net and Molina ride lines; plan question when it changes the number |
| Senior Legal Hotline | Statewide housing resource | Sacramento County residents 60+ only |
| Medicare Savings Programs | Bundled with Medi-Cal and hidden when Medi-Cal = No | Split from the Medi-Cal application; shown regardless of Medi-Cal |
| County mental health lines (incl. Del Norte) | Same patient text for everyone | Patient text follows Medi-Cal status: ongoing care is a Medi-Cal benefit; others go to their MD/plan, with 988 |
| County change with selections | Silently kept out-of-area resources | Conflict blocks copy until removed or kept as an explicit exception (recorded in the note) |
| Staff edits | Lost when a resource was added | Per-resource wording edits survive add, remove and reorder |
| Start over | None | Start new referral clears all encounter state |
| Copy failure | No fallback | Manual copy box with the plain text selected |
| "hungry", "shutoff notice" | 0 results | Suggest Food, Utilities, etc. |
| Patient choice | None | Information only / Help connecting / No help today |
| Status wording | None | "Requested" vs "booked", and "cost question" vs "refill requested", appear only after the staff member confirms the event happened |

## Workflow

1. **What did you hear?** Type a short phrase, then pick the need(s). If there are several, the patient's priority goes first.
2. **Where and coverage.** Choose the county (or "County not listed") and Medi-Cal status. The plan question appears only for rides.
3. **What would the patient like?**
   - **Information only:** the shortest path; it can be a single link or number.
   - **Help connecting:** shows only the routing questions that change the route: timing, home delivery, whether the patient can make calls, and a safe follow-up channel.
   - **No help today:** ends with no message and no automatic referral.
4. **Resources.** Ranked with local services first; a service based in another county appears only if it lists the patient's county. Each card shows intake (unknown by default), review status and sources.
5. **Agreed plan** (help path). Record who acts first, what has actually happened, who follows up and by when, and the backup route. For time-sensitive needs, copying is blocked until an owner, a time and a backup are set, or until "no safe backup" is flagged to the lead.
6. **Safety concern** leaves the routine flow entirely.

## Files

- `index.html`: built app.
- `src/template.html`: app source.
- `data/services.json`: v2 data. Each service is one record with county overrides and carries source, review status, date, maintainer, claims and change history.
- `config/pilot.json`: staff-only pilot settings (roles, referral contact, approved policy text). Everything is null until Sutter approves it.
- `scripts/migrate.py`: v1 → v2 data, plus the source-backed corrections.
- `scripts/build.py`: builds `index.html`.
- `scripts/check_content.py`: checks for retired materials, phone roles, regional services marked statewide, staff/patient contradictions, overdue reviews and missing review metadata. Writes `review-queue.json`.
- `scripts/check_links.py`: link and claim checker for a scheduled job with web access. It only reports; it never marks anything verified.
- `tests/test_v2.py`: end-to-end tests through normal controls (54 checks). Optional accessibility check: `npm install axe-core@4` inside `tmp/`.
- `tests/scenarios.py`: readback and end-to-end scenarios.
- `VERIFICATION.md`: corrections, with the source, the date and the exact claim for each.
- `DECISIONS.md`: open Sutter decisions.

## Run

```
python3 scripts/migrate.py && python3 scripts/check_content.py && python3 scripts/build.py
CHROME_PATH=/usr/bin/google-chrome python3 tests/test_v2.py
```

## Patient-free acceptance checks for an authorized tester

These can't be tested here:
- Paste into a real My Health Online message. Confirm bold text and links survive, and check how it looks on a phone.
- Confirm delivery to a test patient account.
- Read-aloud script: read it to a colleague and see if they can repeat the next step.
