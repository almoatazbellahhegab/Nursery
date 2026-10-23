# Sprint review and branch workflow

1. Refine scope and gate decisions. Split work that cannot meet the exit milestone; no silent acceptance of pending policies.
2. Branch each feature from the current sprint integration branch using its exact branch name in plan.json. Feature branches are created when implementation begins, not as empty placeholders.
3. Commit coherent increments: contract/domain, client behavior, tests, review evidence. Include FEAT/TW/test IDs in commit messages.
4. Merge locally with a merge commit into sprint/NN-review, retaining the feature branch. Do not merge or push main while review is pending.
5. Run changed-area tests, regression, builds and security checks appropriate to the increment. Append immutable run records with UTC time, commit, environment, test ID, result, evidence and defects. Not run, blocked and partial are never pass.
6. Deliver the review URL, Windows launcher, iPhone access instructions, web/mobile differences, UAT steps, test report, release notes and known limitations.
7. User reviews Windows 11 and physical iPhone. Native iOS acceptance is separate from browser preview. Each source acceptance case has a linked UAT ID in plan.json. Automated checks cannot accept UAT.
8. Record the user's explicit sprint confirmation with date, exact wording and approved commit in approvals.json. Only then push the confirmed sprint and feature branches. Approval does not waive specialist gates or authorize production deployment.

S01 preview checks are supplemental UAT-S01 cases. Source product test cases remain Not run because the preview has no real API, authentication, database or native app. Source test IDs are preserved without claiming full-feature coverage.
