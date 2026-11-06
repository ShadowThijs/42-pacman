# Project management

This directory is the evidence of how the Pac-Man project was planned,
tracked, tested and released. It is written so a reviewer can understand
the project in about one minute, then open the document that answers a
specific question.

## One-minute tour

1. **How the work was split**: `team_organization.md`. Two students,
   tlogtenb and asylla, shared ownership by feature area. The table also
   explains that some commits recorded on tlogtenb's account cover joint
   ghost work with asylla.
2. **When the work happened**: `timeline.md`. It shows the original
   phase plan next to the actual milestones reconstructed from the git
   history and weekly checkpoints.
3. **Why the project looks the way it does**: `project_analysis.md`. It
   records the architecture choices, alternatives and trade-offs.
4. **What could have gone wrong**: `risk_analysis.md`. It is a live
   register with probability, impact, mitigation and status.
5. **How progress was measured**: `progress_tracking.md`. It compares
   planned and completed work and records the git history summary.
6. **How quality was checked**: `acceptance_test_plan.md`. Every
   requirement is mapped to an automated test or a manual step, and the
   bugs found during the project are listed with their fixes.
7. **What blocked the team**: `blockers.md`. Each blocking point and
   conflict is recorded with its resolution.
8. **How the game is shipped**: `deployment.md`. It contains the
   PyInstaller build, artifact list and the itch.io upload checklist.

## Document index

| Document | Purpose |
| --- | --- |
| `README.md` | This tour and index |
| `timeline.md` | Planned phases, actual milestones, Gantt view |
| `project_analysis.md` | Scope, architecture and technical decisions |
| `risk_analysis.md` | Risk register and mitigation |
| `team_organization.md` | Roles, decisions, contributions |
| `progress_tracking.md` | Progress against plan and git summary |
| `acceptance_test_plan.md` | Requirements checklist, test mapping and bug log |
| `blockers.md` | Blocking points and conflicts |
| `deployment.md` | Packaging and publication checklist |

## How to use this directory during a review

- Start with `timeline.md` to see the project rhythm.
- Open `team_organization.md` when asked who did what.
- Open `acceptance_test_plan.md` when asked how a requirement was
  verified.
- Open `risk_analysis.md` when asked what could still go wrong.
- Open `deployment.md` when asked how the package was produced.

The documents are deliberately short and factual. Dates and commit
counts come from the repository history. Where a decision was made in a
discussion and not in a commit, the rationale is recorded here.
