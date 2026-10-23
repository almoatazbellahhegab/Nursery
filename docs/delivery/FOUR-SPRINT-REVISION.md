# Four sprint plan revision

Requested change: implement the same content in four sprints. This changes scheduling and grouping, while preserving all original scope, dependency text, branch names, acceptance expectations, decisions, release controls and test history.

| Current sprint | Original sprint milestones | Features | Feature tasks | Technical tasks | Source tests |
| --- | --- | ---: | ---: | ---: | ---: |
| S01 Platform foundations and nursery setup | S01–S04 | 14 | 68 | 37 | 61 |
| S02 Daily operations and Phase 1 release | S05–S07 | 9 | 44 | 18 | 75 |
| S03 Safety, communication, finance and growth | S08–S12 | 12 | 63 | 9 | 55 |
| S04 Advanced and optional modules | S13–S14 | 6 | 29 | 5 | 25 |
| Total | All 14 original milestones | 41 | 204 | 69 | 216 |

The full itemized tasks and milestone exit criteria are in SPRINTS.md. The original plan and checklist are frozen in baselines/14-sprint-plan.json and baselines/14-sprint-SPRINTS.md. Original UAT identifiers remain stable; currentUat aliases identify the new sprint assignments. Historical execution records and the prior push approval remain unchanged.

Durations and dates are to be estimated against the unchanged workload and available capacity. The original two-week planning envelope is not carried over as an eight-week commitment. Separate approvals for advanced/optional modules remain mandatory. Their inclusion in S04 does not close their policy or product gates.

Each sprint still delivers a Windows 11 web review and an iPhone review result, linked tests/UAT, release notes and known limitations. Native-device checks stay separate from browser previews. Feature branches, regular commits and the explicit confirmation-before-push workflow remain in effect. Existing environment/build blockers and incomplete feature statuses are retained.

Regression verification extends RV-001 to compare every previous feature, development task, technical task and test field against the frozen baseline, permitting only reassignment and the corresponding FEAT-036 sprint-status reference. It also verifies that all original milestone content, controls and decisions remain intact. RV-007 checks four portal groups and both stable and current-sprint UAT links.
