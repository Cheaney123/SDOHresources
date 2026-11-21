# Decisions needed from Sutter before the pilot

The app shows "Sutter-approved wording needed" wherever one of these is missing, and doesn't invent a protocol.

1. **Mandated reporting text.** Exact approved steps and roles to show in safety mode (`config/pilot.json → approvedText.mandatedReporting`). The APS number is shown; the procedure is not.
2. **Urgent escalation.** Who is paged or called, and how, when a safety concern comes up during a routine call (`approvedText.urgentEscalation`).
3. **Mood screening.** Confirm that "routine positive mood screens go to AI-CBT; behavioral health outliers go to the social worker" is current approved workflow (`approvedText.moodScreening`).
4. **Time-sensitive medication access.** The approved path for an imminent refill gap, and who can place a refill versus a cost question (`approvedText.medicationAccess`). Also confirm the pharmacy team's cost sequence: HealthWell, then Cost Plus Drugs, then the manufacturer program.
5. **Roles list.** Which roles may be named as owners in patient copy. Current defaults: staff member, pharmacy team, social worker, nurse, pilot referral contact.
6. **Pilot referral contact and backup.** Name, monitored hours, and the patient-facing wording for a monitored contact. None is configured, so the app flags the gap rather than offering a contact.
7. **Callback number for patients.** Is there an approved, monitored number patients can call back? If not, "Patient will call us" can't be offered.
8. **Coverage and monitoring.** Who watches follow-ups promised in the app ("I will follow up by tomorrow"), and what happens when the owner is out.
9. **Case tracking.** Confirm that the existing EHR workflow records preference, referral activity, recipient acknowledgment and service receipt. This guide deliberately stores none of it.
10. **Translations.** The process for reviewed translations of patient wording (none are approved yet). The app shows English only.
11. **Corrections inbox.** The email or queue for "Report a correction" (`correctionsEmail`). The app currently produces copyable text only.
12. **Hosting.** Stay on Cloudflare Workers / GitHub Pages, or move to a Sutter-managed host. Production deployment is left to the project owner.
13. **Plan benefits.** Approved wording for checking Medicare Advantage, SutterSelect and Sutter Health Plan benefits (rides, meals, OTC) before community resources.
14. **Senior Legal Hotline.** Confirm the service area directly with LSNC.

## Gaps from the blind readbacks that wording can't close

15. **Same-day food after hours.** No verified phone option for food tonight beyond 2-1-1 (whose hours aren't verified in this guide) and the web-only Food Finder.
16. **Same-day rides.** Plan rides need 3–5 business days' notice and paratransit needs approval. There's no verified same-day ride option, and none for patients without Medi-Cal.
17. **Missed callbacks for patients who can't make calls** and allow no voicemail or MHO: what staff do after repeated missed calls.
18. **A team number for "if you don't hear from us".** Without an approved, monitored number, a missed staff follow-up leaves the patient no way back in (see item 7).
