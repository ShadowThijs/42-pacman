# Progress tracking

## Where we ended up

| Area | State | Notes |
| --- | --- | --- |
| Repository and tooling | Done | Python project, Makefile, uv and pip install paths |
| Config parser and CLI | Done | Comments, defaults, clamping and one-argument CLI |
| Maze integration | Done | A-Maze-Ing 2.0.2 wheel, bitmask rendering and collision |
| Player movement | Done | Buffered input, wall collision, reverse at any point |
| Ghosts | Done | Four types, chase targets, fright, eaten eyes and respawn |
| Pellets | Done | Normal pellets, four corner power pellets and scoring |
| Game flow | Done | Menu, game, pause, death, game over, victory, leaderboard |
| Highscores | Done | SQLite, top ten, name rules and persistence |
| Cheats | Done | Invincible, speed, freeze, extra lives and level skip |
| Testing | Done | 38 headless tests plus a manual play script |
| Packaging | Done | PyInstaller spec, CI matrix and local smoke test |
| Documentation | Done | README and this folder |
| itch.io upload | Pending | Needs the team account |

## Progress by phase

| Phase | What we had at the end of it | Still missing at that point |
| --- | --- | --- |
| Setup | Repository and environment | Everything else |
| Config and maze | Config loader and first maze | Game loop, player, ghosts |
| Movement | Pac-Man moving and eating pellets | Ghost behaviour and screens |
| Ghost foundation | Ghost classes and targets | Collision, fright and respawn |
| Ghost integration | Ghosts moving on the real maze | Screens and score flow |
| Screens | Menu, game, pause and score screens | Cheats, timer and victory |
| Cheats and fright | Super-pacgums and cheat mode | Timer, victory and polish |
| Timer and packaging | Level timer, victory screen and CI build | Final fixes and documentation |
| Final pass | Config `level`, instructions, tests and docs | itch.io upload |

## Time distribution

The commit history shows the shape of the project better than a weekly
diary:

- June: setup only.
- July: configuration, maze, rendering and first movement.
- August: sprites, movement polish, ghost skeleton and a long pause.
- September: almost no commits because of other coursework.
- October: the main gameplay push, including ghost classes, collision,
  fright, screens and cheats.
- November: timer, victory, packaging, tests, documentation and the
  final config fixes.

There are more than 80 commits. Most are under tlogtenb's account and 15
are under asylla's. Some commits under tlogtenb's account include joint
work with asylla on the ghost code.

## Quality status at the end

| Check | Result |
| --- | --- |
| `make lint` | Pass |
| `make lint-strict` | Pass |
| `make test` | 38 tests pass |
| Headless play and screen render | Pass |
| Invalid config battery | Pass, no traceback |
| Packaged executable smoke test | Pass |
| CI build matrix | Linux, Windows and macOS build |

## What is left

1. Run the final `make lint`, `make lint-strict`, `make test` and
   `make package` on the committed tree.
2. Upload the package to the unlisted itch.io page using
   `deployment.md`.
3. Add the public URL to the project page.
4. Run through the manual script in `acceptance_test_plan.md` with the
   packaged build.

The upload is the only part that cannot be finished inside the
repository.
