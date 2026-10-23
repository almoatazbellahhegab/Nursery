# Sprint 1 supplemental checks

These checks validate only the offline delivery tools and presentation experiments. They do not pass the 216 source product cases, which remain Not run in plan.json. Each source test has a stable linked UAT ID and its original preconditions, steps and expected result.

| Test | Automated behavior | UAT link | Source relationship |
| --- | --- | --- | --- |
| RV-001 | All source identifiers retained once; valid sprint assignments, dependencies and UAT links | UAT-S01-04 | TW-011 and traceability |
| RV-002 | Matching, nonempty English and Arabic catalogue keys | UAT-S01-03 | Partial FEAT-036-05 groundwork |
| RV-003 | Invalid evidence and native-app pass rejected | UAT-S01-05, UAT-S01-06 | Review integrity |
| RV-004 | Review routes, private-file denial, origin validation, durable append-only results | UAT-S01-05 | Delivery tooling only |
| RV-005 | Desktop navigation and Arabic direction in an actual browser | UAT-S01-01, UAT-S01-03 | Partial TW-034 prototype |
| RV-006 | Mobile viewport, parent/staff switching and Arabic layout | UAT-S01-02, UAT-S01-03 | Partial TW-035 prototype; emulation only |
| RV-007 | Review log saves safely and survives reload; source mapping appears | UAT-S01-04, UAT-S01-05 | Review workflow |

## Manual acceptance steps

- UAT-S01-01: On Windows 11 open the dashboard, inspect all four navigation views, keyboard focus and 200% zoom.
- UAT-S01-02: On physical iPhone Safari open the computer's Wi-Fi URL, inspect mobile views, switch parent/staff and bottom tabs; rotate device and check touch targets.
- UAT-S01-03: In both clients switch to Arabic and back; inspect layout and mixed-direction values. Arabic quality requires a human language owner.
- UAT-S01-04: Expand a sprint, find a DEV and TC identifier, compare original expected result with the workbook and inspect the linked UAT ID.
- UAT-S01-05: Save a synthetic observation, reload and download the log. Confirm case, device, UTC timestamp and result.
- UAT-S01-06: Native iPhone build is Blocked until SDK, macOS/Xcode, signing and device installation are available.

## Evidence rules

Automated run records under `runs/` contain UTC time, Git code commit, environment, command and result. Human observations live in ignored `review-results/uat.jsonl`; export and retain them with a reviewed sprint handoff, after removing sensitive information. A user check is Pending until the user performs it. Failures get DEF-S01-NNN IDs and an explicit regression test. A green automated run cannot authorize push or pass manual UAT.
