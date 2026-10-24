# Little Garden client demo

This is a fictional nursery day built into the actual Next.js and Flutter web
clients. It is designed for a client presentation without manual data entry.
Every name, invoice, amount and event is synthetic.

## What is included

- Two branches: Maadi Garden and New Cairo Grove.
- Four classrooms, eight educators, 24 children and 24 fictional family records.
- Per branch: 12 enrolled, capacity 20, eight present, two expected, one went home
  and one absent at the starting snapshot.
- 48 seeded daily events: arrival, breakfast and learning activities.
- 24 tuition invoices in integer minor units: paid, partially paid and unpaid.
- Six admissions leads with owners, age groups and next steps.
- Four branch notices and four guided web demo stories.
- English/Arabic labels, RTL layouts, local mutations and deterministic reset.

Snapshot: 24 October 2026, 11:30, Africa/Cairo. Each branch starts with fictional
EGP 54,000 billed, EGP 36,000 paid and EGP 18,000 outstanding. These values are
illustrative, not revenue or collection performance from a real customer.

## Data and reset

`demo/seed.json` is the canonical fixture. Run `node tools/generate-demo.mjs` to
refresh the web JSON and Dart fixture. `node tools/generate-demo.mjs --check`
validates references, branch/classroom associations, money invariants, UTF-8
Arabic labels and parity between both clients. Never substitute real records.

Reset demo restores the starting records and clears local attendance/care edits,
follow-up previews and scheduled sample visits. Reloading also resets the demo.
Mobile roles share local state so staff-to-parent storytelling works in one app
session. Web and mobile mutations do not synchronize across devices or tabs.

The selectors are presentation filters. They do not demonstrate authenticated
branch or family access. There is no operational database seeding, message
sending, payment processing or enrollment conversion. FEAT-041 source API and
security acceptance remains Not run until its predecessors and real services exist.

See [the client presentation script](../docs/runbooks/client-demo.md) for the
business stories, expected outcomes, UAT checklist and known limitations.
