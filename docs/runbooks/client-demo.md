# Client presentation: one nursery day, four business stories

## Ready-to-present links - 2026-10-24

- Dashboard business presentation: http://localhost:3300/demo
- Mobile parent presentation: http://192.168.8.154:3400/?view=parent
- Mobile educator presentation: http://192.168.8.154:3400/?view=teacher
- Connected dashboard: http://localhost:3300/
- Connected Flutter web application: http://192.168.8.154:3400/

The phone must use the same Wi-Fi as the development PC, which must remain on.
The Wi-Fi address can change; `Start-Applications.cmd` prints the current address.
The presentation links need no login and contain only fictional Little Garden
records. Start with Reset demo. Guided web stories select Maadi Garden so the
named examples below are available. Allow about eight minutes for the four stories.

The connected links require sign-in. Generated local credentials remain in the
ignored `.tools/dev-accounts.json`; use administrator, branch_manager and teacher
accounts for the corresponding business roles. Do not show the credential file
or authenticator setup/recovery material during a presentation or screen recording.

### What is connected and what is simulated

| Business capability | Demonstration status |
| --- | --- |
| Sign-in, current organization/role/branch access | Connected API and PostgreSQL |
| Branch details, activation and member assignments | Connected web and Flutter administration |
| Staff attendance, corrections, history and daily report | Shared persisted state across web and Flutter |
| Authenticator enrollment and one-use recovery | Connected account security in both clients |
| Child/classroom overview, child attendance and daily care stories | Fictional local presentation |
| Parent summary, notices, fee follow-up and admissions visit story | Fictional local presentation |
| English/Arabic and RTL | Available in both experiences |

Provider-backed Google/Apple/phone sign-in, remaining product modules and native
iPhone delivery are not claimed ready. The live demo uses the tested compiled
checkpoint; later authentication/rotation work in the working tree is not yet
included in these compiled artifacts. The broader fictional stories do not
synchronize between devices. Only the connected staff workflow shares persisted
state. These are local/same-Wi-Fi links, not public internet hosting.

Direct mobile views use `/?view=parent` and `/?view=teacher` on the printed
mobile address. On the host PC, use `http://localhost:3400/?view=parent` or
`http://localhost:3400/?view=teacher`. The Teacher link opens educator tools
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

Latest automated presentation verification: all nine groups pass in
`docs/testing/runs/2026-10-24T17-27-41-681Z-demo-browsers.json`. The dashboard and
mobile links return HTTP 200, including the current Wi-Fi address. Physical phone
reachability and human acceptance are still separate checks.

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

The four fictional business stories above are in-memory simulations. No authentication, PostgreSQL/RLS,
server synchronization, durable audit, real notifications, payments, enrollment,
media, medical, pickup or transport workflow is connected. Policy gates remain
open. All financial figures are explicitly demo-only. Demo data is not inserted
into production storage or real commercial metric inputs.

FEAT-041 gains fictional dataset and presentation/reset groundwork. Its four
source cases TC-FEAT-041-01 through TC-FEAT-041-04 retain their API-integration
acceptance status of Not run. The user later waived outstanding reviews for
implementation/testing; this does not accept UAT. The presentation is not a
completed operational release of those features.

The fictional presentation remains on retained `feat/FEAT-041-demo-scenarios`
history and is served alongside the connected runtime. Connected staff, branch and
MFA increments are committed and integrated locally through `1678307`. Later
identity/provider changes remain in progress. No new push, public deployment,
native iPhone build or human UAT is implied by the presentation links.
