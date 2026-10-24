# Client presentation: one nursery day, four business stories

Open the dashboard using `Start-Applications.cmd`. Use its printed mobile link
on the same Wi-Fi. Both actual compiled clients contain the fictional Little
Garden dataset. Start with Reset demo. Guided web stories select Maadi Garden
so the named examples below are always available. Allow about eight minutes.

Direct mobile views use `/?view=parent` and `/?view=teacher` on the printed
mobile address. On the host PC, use `http://localhost:3200/?view=parent` or
`http://localhost:3200/?view=teacher`. The Teacher link opens educator tools
immediately, and Reset retains the view chosen by the link. A phone must use
the PC's Wi-Fi address; localhost on the phone refers to the phone itself.

## 1. A calmer start to the nursery day — two minutes

Audience: nursery owner, branch manager, front-office team.

- On Overview, point to eight children here out of 12, two classrooms and
  12 enrolled out of 20 available places. Explain that each number comes from
  the displayed branch records.
- Select Start the morning story. Find Farida Demo and choose Check in.
- Return to Overview: attendance is now nine of 12. Open Daily care and choose
  Farida: an arrival entry appears with its time and educator.
- Switch to New Cairo Grove: the roster and classroom team change. Its
  attendance stays eight of 12. Explain this is a presentation filter, not
  evidence of production access control.

Value conversation: How does the nursery currently reconcile arrivals and
classroom lists? Where does the team lose time finding the latest information?
The demo shows one consistent local attendance/timeline update; it makes no
claim about measured time savings or implemented pickup authorization.

## 2. Give families a reassuring daily picture — two minutes

Audience: parents, educators, nursery manager.

- Reset. On mobile, show Adam Demo's parent summary and open Timeline. Point to
  arrival at 08:15, breakfast at 09:10 and garden-building at 10:20.
- Change Demo experience to Staff. Choose Add sample care update.
- Switch back to Parent and view the timeline: the garden-play update appears
  in the same app session. Acknowledge that separate web/mobile sessions do not
  synchronize; the demonstration starts from matching fixtures.
- Open Notices for the branch's learning theme and family reading morning.
- Switch to Arabic to show readable Arabic text and RTL layout.

Value conversation: What questions do families repeatedly ask at pickup? What
would an informative day summary help the classroom team communicate?

## 3. Make fee follow-up visible — two minutes

Audience: owner, finance and administration.

- Reset the web demo and open Fees & follow-up. Six invoices need follow-up;
  the branch's outstanding tuition is EGP 18,000.
- Find Youssef Demo, invoice INV-26-003: EGP 4,500 tuition, EGP 3,000 paid,
  EGP 1,500 outstanding. These reconcile with the dashboard total.
- Choose Preview reminder and review the amount and wording. Choose Record
  demo follow-up. The row now says Previewed locally. Nothing is sent.
- Turn off Outstanding invoices only to see all 12 branch invoices, including
  paid invoices. On mobile, choose Youssef to show that family's invoice summary.

Value conversation: How does the office decide whom to contact, and how does
it avoid following up families whose tuition is already paid? No collection-rate
improvement or real payment processing is claimed by this demo.

## 4. Give each inquiry an owner and next step — two minutes

Audience: nursery owner, admissions and front-office team.

- Reset, open Admissions and find Amira's family. Point to the owner, inquiry
  source, age group and next action.
- Choose Schedule sample visit. A 27 October, 10:00 sample appointment appears
  and the next action becomes welcoming the family.
- Explain the potential benefit of consistent inquiry follow-up. The demo
  schedules locally, sends no invitation and creates no child enrollment.
- Finish with Reset demo, returning every story to its baseline.

## Presentation acceptance checklist

- [ ] Windows 11 interactive browser: complete all four stories; record reviewer,
  outcome and observations separately from automated headless results.
- [ ] Physical iPhone Safari: open the same-Wi-Fi mobile URL, complete the
  parent/staff story, switch branches/children, inspect Arabic in portrait and
  landscape, and confirm Reset demo restores the baseline.
- [ ] Native iPhone: repeat after a signed macOS/Xcode build and installation.
- [ ] Emulated browser: automated evidence under `docs/testing/runs/*demo*`.
- [ ] Arabic language quality: obtain named reviewer feedback.
- [ ] Client presentation sign-off: record feedback without accepting operational
  feature UAT or treating demo selectors as permission boundaries.

## Known limitations and source mapping

These are in-memory presentation simulations. No authentication, PostgreSQL/RLS,
server synchronization, durable audit, real notifications, payments, enrollment,
media, medical, pickup or transport workflow is connected. Policy gates remain
open. All financial figures are explicitly demo-only. Demo data is not inserted
into production storage or real commercial metric inputs.

FEAT-041 gains fictional dataset and presentation/reset groundwork. Its four
source cases TC-FEAT-041-01 through TC-FEAT-041-04 retain their API-integration
acceptance status of Not run. The original dependency and policy gates are not
waived. The demo is not a completed operational release of those features.

The requested feature branch is `feat/FEAT-041-demo-scenarios`. This session's
`.git` is read-only, so the changes are uncommitted in the existing working tree;
no feature branch creation, merge or push is claimed. Preserve prior uncommitted
S03 verification work and exclude the pre-existing untracked attendance evidence.
