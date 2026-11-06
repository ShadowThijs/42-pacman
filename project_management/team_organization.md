# Team organization

## Team

| Student | Main part of the work |
| --- | --- |
| tlogtenb | Project setup, config, maze integration, movement, state stack, UI, database, cheats, packaging, CI and tests |
| asylla | Ghost classes and targets, frightened state, super-pacgums, collision, eaten-ghost behaviour and gameplay testing |

We split the work by file and feature. One person usually wrote a
feature, the other reviewed it and played the build. The ghost work was
shared more closely: tlogtenb wrote the early base class and later
pathfinding refactor, asylla wrote most of the ghost class and the four
targets, and we pair-programmed several of the collision, fright and
freeze fixes.

## How we worked

- We kept a shared task list with the next feature and the next bug.
- Before starting a change that touched `Game`, `Ghost` or the state
  stack, we told the other person, because those files were used by both
  of us.
- We reviewed each other's commits before merging and played the game
  after large changes.
- When we disagreed, we tried the simpler option first and kept it only
  if it survived a play session and the tests.
- We used the commit history as the main record of what changed. That is
  why the timeline and contribution table are based on it.

## Where the time went

Most of the code was written in July, August and October. September was
mostly quiet because of other coursework. The ghost collision and
fright work was finished in October, and the timer, victory flow,
packaging and documentation were finished in early November.

The full history has more than 80 commits. Most are recorded under
tlogtenb's account and 15 are recorded under asylla's. Some commits under
tlogtenb's account cover pair-programming sessions with asylla on ghost
collision, frightened behaviour and freeze edge cases. The table below
describes the work, not the commit count.

## Contribution table

| Area | tlogtenb | asylla |
| --- | --- | --- |
| Repository, dependencies and Makefile | Wrote and maintained | Review |
| Config parser, defaults and CLI | Wrote and tested | Reviewed the config format |
| Maze package integration and wall rendering | Wrote | Reviewed the bitmask use |
| Pac-Man movement, input buffer and wall collision | Wrote | Playtested and reported edge cases |
| Ghost base class and four ghost types | Wrote the early base class and refined pathfinding | Wrote most of the ghost class and the four targets |
| Frightened mode and super-pacgums | Connected it to the game loop | Wrote the frighten state and collision changes |
| Eaten ghosts, eyes and respawn | Refactored the state handling | Co-developed and playtested |
| State stack and screens | Wrote the state manager, screens and theme | Playtested and reviewed the flow |
| Highscore database | Wrote the SQLite layer | Tested persistence and name entry |
| Cheat mode | Wrote the cheat state and hotkeys | Playtested every cheat |
| Level timer and victory flow | Wrote | Tested the full game cycle |
| Packaging and CI | Wrote the spec and workflow | Smoke-tested the builds |
| Project management documents | Wrote the first draft | Reviewed and corrected the contribution record |
| Tests | Wrote the pytest suite | Wrote the manual acceptance cases |

## Bugs we fixed together

- The config `level` value was loaded but never used, so every game
  started at level 1.
- A pellet could be placed on a tile that was not reachable from the
  spawn, which made a level impossible to finish.
- Freezing a frightened ghost could make it dangerous again.
- The extra-life cheat stopped working once the player had three lives.
- Saving a score opened the leaderboard instead of returning to the main
  menu.
- The first level was not fully reproducible because pellet placement
  used the global random state.

## How we resolved disagreements

We did not have a formal voting process. If we disagreed on a design
choice, we looked at which option was easier to test and explain. For
example, we kept the flat config because it was easier to clamp and
document than a nested per-level structure. We kept the state stack
because it made pause and death overlays much simpler than mode flags.
If a choice did not work in a play session, we changed it, even if it
was already merged.
