# Team organization

## Team

| Student | Role | Main responsibility |
| --- | --- | --- |
| tlogtenb | Technical lead and integrator | Architecture, configuration, maze integration, player movement, state stack, UI, database, cheats, packaging, CI, documentation and automated tests |
| asylla | Gameplay lead | Ghost class foundation, per-ghost targets, frightened state, super-pacgum interaction, collision and eaten-ghost behaviour, gameplay validation |

The project was a two-student collaboration. Both students reviewed
each other's work and both are expected to explain any module in review.

## How decisions were made

- **Feature ownership**: each feature had one owner who made the final
  call, with the other student reviewing.
- **Architecture decisions**: discussed in the weekly checkpoint and
  recorded in `project_analysis.md`. A decision was accepted when both
  students could explain the trade-off.
- **Interface changes**: announced before merging, because a change to
  `Game`, `Ghost` or `State` affects both students.
- **Bug triage**: a bug that blocks play or the build is fixed first. A
  cosmetic bug is added to the backlog.
- **AI usage**: AI suggestions were treated as proposals. The author
  had to understand, run and test every accepted suggestion.

## Communication

- Short asynchronous messages during the week for interface changes and
  blockers.
- A weekly checkpoint to compare progress against the plan and update
  `timeline.md` and `risk_analysis.md`.
- A face-to-face integration session before packaging and before the
  final compliance pass.
- Git commits are small and use a `feat:`, `fix:`, `chore:`, `perf:`,
  `refactor:`, `build:` or `docs:` prefix.

## Issue handling

1. Reproduce the issue and write down the smallest failing scenario.
2. Assign an owner.
3. Add or update an automated test when the issue is in Python logic.
4. Fix the root cause, not the symptom.
5. Run `make lint`, `make lint-strict` and `make test`.
6. Commit with a message that describes the behaviour change.

Examples from the project:

- The starting level was always 1 because `Config.level` was loaded but
  never used. The fix moved `level` into `Game.start_new_game` and added
  `test_start_uses_configured_level`.
- Pellet placement sampled the whole walkable set, which could put a
  pellet behind an unreachable wall. The fix computes a reachable set
  from the player spawn first.
- Extra lives were capped at three, so pressing the cheat key at the
  start did nothing. The fix allows repeated extra lives up to the safe
  maximum.
- The name prompt originally opened the leaderboard after saving. The
  required game loop ends at the main menu, so the flow now returns to
  the main menu and shows the saved score there.

## Contribution ownership

| Area | tlogtenb | asylla |
| --- | --- | --- |
| Repository, tooling and dependency management | Lead | Review |
| Configuration parser, defaults, clamping and CLI | Lead | Testing and review |
| A-Maze-Ing integration and maze rendering | Lead | Review |
| Pac-Man movement, input buffer and wall collision | Lead | Testing and review |
| Ghost class foundation | Integration and pathfinding refinement | Lead, original class and per-ghost targets |
| Frightened mode and super-pacgum interaction | Game-loop integration | Lead, frighten state and collision logic |
| Eaten-ghost eyes, respawn and freeze | Lead, state refactor | Co-development and gameplay validation |
| State stack, screens, theme and HUD | Lead | Playtesting and review |
| SQLite highscores and persistence | Lead | Persistence testing |
| Cheat mode and review usability | Lead | Playtesting |
| Level timer, victory screen and progression | Lead | Testing and review |
| Packaging, CI and release artifacts | Lead | Smoke testing |
| Project management documents | Editor and co-author | Co-author |
| Automated tests | Lead | Acceptance testing |

### Commit record note

The git history contains 65 commits recorded under tlogtenb's account
and 15 commits recorded under asylla's account at the final compliance
pass. Some commits recorded on tlogtenb's account cover pair-programming
sessions with asylla on ghost collision, frightened behaviour and freeze
edge cases. The contribution table therefore describes ownership of the
work, not raw commit counts.

## Definition of done

A feature was considered done only when:

- it is implemented in the repository;
- it has type hints and a docstring;
- `make lint` passes;
- an automated test exists, or a manual acceptance step is written in
  `acceptance_test_plan.md`;
- the other student has played with it or reviewed the diff;
- the README or the instructions screen explains it if a user can see
  it.
