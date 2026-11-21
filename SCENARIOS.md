# End-to-end scenarios (synthetic, run through the normal controls)

Full outputs are produced by `tests/scenarios.py` and written to `tmp/scenarios/`.

| Scenario | Staff decision | Patient's first action | Follow-up owner | Unresolved approval |
|---|---|---|---|---|
| **Technician:** refill unaffordable, due soon | Help connecting. Cost question sent to the pharmacy team (confirmed). Not a refill order. Backup: HICAP. | None needed. The pharmacy team acts first. The patient is told to call their pharmacy or doctor today if about to run out. | Pharmacy team, by tomorrow, through MHO | Approved time-sensitive medication workflow; who may place a refill |
| **Pharmacist:** tomorrow's ride fell through | Help connecting, timing today. The plan is unknown, so the patient calls member services or their plan's ride line and says the ride is needed soon. The app warns that plan rides usually need 3–5 business days. | Call the plan about a ride. If no ride in time, call the doctor's office to reschedule. | Staff member, later today, by phone; retry later that day. No same-day backup exists, so the gap is flagged to the lead. | Same-day ride path; plan-benefit wording for Medicare Advantage |
| **Dietitian:** groceries needed tonight | Help connecting, timing today, no home delivery. The app warns to confirm a site is open today. | Call 2-1-1 tonight. If that doesn't work today, use the Food Finder. | Staff member, later today, by phone in the patient's safe evening window; retry the next business day | Monitoring of staff follow-ups; whether a same-day food contact exists |
| **No MHO or reliable internet;** first agency couldn't help | Help connecting. Plan read aloud by phone. The first agency is marked "already tried", so it isn't repeated as the first step. No safe backup, so the gap is flagged to the lead. | Call 2-1-1. Otherwise, call the customer service number on the utility bill. | Staff member, next week, by phone with no voicemail | Pilot referral contact and backup; approved callback number |
| **Immediate safety concern** | Leaves the routine flow. No resource message. The staff note says escalation follows the approved workflow. | Safety contacts (911, 988, APS) | Per approved workflow | Mandated-reporting and urgent-escalation wording |

**Information-only control:** the patient has food this week and only wants the CalFresh application. The output is one short message with the BenefitsCal link, no fallback section and no follow-up questions.

**Voluntary decline:** no patient message, no automatic social work referral. The note says the need was not ruled out.
