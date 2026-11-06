# Progress tracking

Progress was checked at the end of each work week. The table compares the
plan from `timeline.md` with what was actually completed. The remaining
work at each checkpoint was carried into the next week or explicitly
moved out of scope.

## Phase status at the final compliance pass

| Phase | Planned | Completed | Status |
| --- | --- | --- | --- |
| P0 Repository and environment | 100% | 100% | Done |
| P1 Configuration and maze loading | 100% | 100% | Done |
| P2 Rendering and pellets | 100% | 100% | Done |
| P3 Actors and movement | 100% | 100% | Done |
| P4 Ghost behaviour | 100% | 100% | Done |
| P5 Screens and game flow | 100% | 100% | Done |
| P6 Cheats and polish | 100% | 100% | Done |
| P7 Progression and timer | 100% | 100% | Done |
| P8 Packaging and CI | 100% | 100% | Done |
| P9 Final compliance and documents | 100% | 100% | Done |
| Itch.io publication | 100% | 0% | Manual team step, artifacts ready |

## Weekly log

| Week starting | Planned work | Completed work | Carry-over |
| --- | --- | --- | --- |
| 2026-06-15 | Repository, Python environment, first commit | Repository, dependency setup, initial README | None |
| 2026-07-20 | Config parser, maze generator integration | Comment-aware JSON loader, first `MazeGenerator` call, mypy fix | Rendering |
| 2026-07-27 | Rendering, player and ghost placeholders | Bitmask rendering, pellets, player and ghost class skeletons | Movement polish |
| 2026-08-03 | Movement, sprites, wall collision, ghost targets | Animated Pac-Man, wall collision, input buffer, pellet score, per-ghost targets | Ghost integration |
| 2026-08-17 | Ghost base class and interaction | Position model, ghost base class, sample interaction, reference examples | Ghost behaviour integration |
| 2026-10-12 | Resume ghost work after course break | Ghost classes, mypy fixes | Collision and fight integration |
| 2026-10-19 | State manager, UI foundation | State manager, theme manager, arcade screens, ghost targeting integration | Screens and flow |
| 2026-10-26 | Death flow, score screens, ghost collision | Respawn timing, ghost release schedule, collision loop, arcade screens | Highscore flow |
| 2026-10-29 | Super-pacgums, frightened state, cheats | Super-pacgums, frighten state, fright timer, collision fixes, Konami cheat, invincibility, speed, freeze | Extra lives, HUD |
| 2026-11-02 | Freeze edge cases, rendering performance, timer | Frozen ghost identity, render caching, frame clearing, corner power pellets, level timer, victory screen | Timer polish |
| 2026-11-03 | Packaging, CI, final polish | PyInstaller spec, CI matrix, artifact upload, HUD fixes, timer start on input | Final compliance |
| 2026-11-06 | Compliance pass | Config `level` fix, instructions screen, project management documents, tests, README, final lint | Itch.io upload |

## Completed work by area

| Area | State | Evidence |
| --- | --- | --- |
| CLI with exactly one config argument | Complete | `pac-man.py`, usage messages, `docs` and tests |
| Comment-aware JSON configuration | Complete | `src/models.py`, config tests |
| Defaults, clamping and unknown keys | Complete | `Config._validated`, config tests |
| A-Maze-Ing integration | Complete | `src/game.py`, pinned wheel, maze generation tests |
| Fixed first level and random later levels | Complete | `new_level(seeded=...)`, determinism test |
| Pac-Man movement and wall collision | Complete | `src/player.py`, wall tests |
| Four ghosts and targets | Complete | `src/ghost.py` |
| Frightened, eaten and respawn behaviour | Complete | Ghost state machine, ghost tests |
| Pacgums and super-pacgums | Complete | Game update loop, scoring tests |
| Score and HUD | Complete | `GameScreen`, `test_eating_pacgum_increases_score` |
| Level progression and timer | Complete | `Game.complete_level`, timer tests |
| Pause, game over and victory | Complete | UI state tests |
| Main menu and instructions | Complete | `StartMenuScreen`, `InstructionsScreen` |
| Persistent top-ten highscores | Complete | `src/db.py`, database tests |
| Cheat mode | Complete | `src/cheats.py`, UI hotkeys, cheat tests |
| Packaging and CI | Complete | `42-pacman.spec`, workflow, package build |
| Project management documents | Complete | This directory |
| Itch.io page | Pending | External upload by the team |

## Git history summary

At the final compliance pass the repository contains 83 commits:

- 68 commits recorded under tlogtenb's account, including merge commits
  and pair-programming sessions with asylla on ghost work;
- 15 commits recorded under asylla's account.

The history is split into small behaviour-focused commits. The main
integration points are:

- configuration and maze loading in July;
- movement, sprites and ghost classes in August;
- ghost interaction and super-pacgums in October;
- state manager and screens in October;
- cheats, freeze, timer and victory in late October and early November;
- packaging, documentation and tests in November.

## Current quality status

| Check | Status |
| --- | --- |
| `make lint` | Pass, no flake8 or mypy errors |
| `make lint-strict` | Pass, no mypy strict errors |
| `make test` | 37 tests pass |
| Headless UI smoke test | Pass |
| Invalid config scenarios | Pass, defaults and clamps logged |
| Packaged executable smoke test | Pass |
| CI build matrix | Linux, Windows and macOS build successfully |

## Remaining work before submission

1. Re-run `make lint`, `make lint-strict`, `make test` and
   `make package` on the final commit.
2. Upload the package to the unlisted itch.io page using
   `project_management/deployment.md`.
3. Add the public URL to the release notes or the project page.
4. Do a final read-through of the README with both students.
