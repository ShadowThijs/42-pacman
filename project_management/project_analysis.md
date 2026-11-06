# Project analysis

## Goal

Build a complete, playable Pac-Man game in Python 3.10 or newer, using an
external maze generator, a simple graphical library, a persistent
highscore system, a polished UI, a cheat mode and a reproducible
packaging pipeline.

## Scope

### In scope

- Main menu, instructions, highscores, pause, game over and victory.
- Ten levels by default with a per-level timer.
- Pac-Man movement with buffered input and wall collision.
- Four ghosts with distinct chase targets, frightened behaviour and
  respawn.
- Normal and super pellets with configurable scoring.
- Persistent top-ten leaderboard.
- Comment-aware JSON configuration with defaults and clamping.
- Cheat mode for peer review.
- PyInstaller package and multi-platform CI.
- Project management documents and an acceptance test plan.

### Out of scope

- Networked multiplayer.
- Sound and music. The original arcade sounds are not reproduced.
- Mobile and web builds.
- Reimplementing the external maze generator.
- Online leaderboards. Scores are local to the machine.

## Constraints

- The maze generator is an external dependency and is used as-is.
- The maze generator is configured with `perfect=False`.
- Python 3.10 or newer and flake8 plus mypy must pass.
- No Python traceback may reach the user.
- The game must remain playable with a malformed configuration.
- The package must be reproducible from the repository.

## Architecture decisions

| Decision | Alternatives considered | Why this was chosen | Trade-off |
| --- | --- | --- | --- |
| pygame as the graphics layer | MLX, tkinter, arcade | pygame is available on Linux, Windows and macOS, supports SVG sprites through SDL_image, and is the common choice for 42 Python game projects. | pygame is a dependency outside the standard library. |
| State stack for screens | One large game loop with mode flags | Overlays such as pause and death are natural when every state is drawn and only the top state updates. | Slightly more indirection when tracing a transition. |
| Flat JSON configuration | Nested per-level array | A flat file is easy to document, easy to clamp and easy to edit during a demo. | Per-level overrides are not supported. |
| SQLite for highscores | JSON file, plain text, pickle | Atomic commits, deterministic ordering with `ORDER BY`, a strict `LIMIT` and no custom parser. | The database file is binary and not human-readable. |
| Bitmask maze cells shared with the generator | Convert the maze to a separate grid | The generator already publishes wall bitmasks. Reusing them avoids a lossy conversion and keeps rendering and collision consistent. | The game is coupled to the generator's bit values, which are documented. |
| Breadth-first ghost pathfinding | Random walk, greedy distance, A* | BFS gives a shortest path in an unweighted corridor graph and is fast enough for four ghosts at 60 FPS. | No weighting for travel time or risk. |
| Dedicated level RNG | Global `random` only | The generator seeds the global RNG internally. A local `random.Random` keeps pellet placement reproducible for the fixed first level. | Two RNG sources must be kept in mind. |
| PyInstaller one-file plus CI matrix | zipapp, Nuitka, manual builds | One file is easy to distribute, and the GitHub Actions matrix proves the build on three operating systems. | One-file startup is slower because the bundle is unpacked. |

## Data flow

1. `pac-man.py` validates the CLI, loads `Config`, opens `Database` and
   creates `Game`.
2. `App` resets the state stack to the main menu.
3. Starting a game calls `Game.start_new_game`. The configured `level`
   becomes the first level number. `new_level(seeded=True)` builds the
   first maze from the configured seed.
4. `Game` creates Pac-Man at the walkable tile nearest the maze centre,
   computes the reachable tile set, places normal pellets on reachable
   tiles and places one power pellet at each corner.
5. `GameScreen.update` advances the timer, Pac-Man, pellets, ghosts,
   collisions and level completion.
6. On death, `DyingState` plays the animation over a frozen frame. On
   game over or victory, `NameEntryScreen` collects a name, the database
   stores the score and the app returns to the main menu.
7. `Game.run` closes the database and pygame on exit.

## Configuration model

The configuration is stored in a flat dictionary. Each key has a typed
default and, for numbers, a safe range. Loading follows this order:

1. Read the file with UTF-8 BOM tolerance.
2. Remove `#`, `//` and `/* */` comments while preserving comment
   markers inside strings.
3. Parse JSON and require an object at the root.
4. Report unknown keys and ignore them.
5. For each known key, use the value if the type is correct, clamp it if
   it is out of range, or use the default if it is unusable.
6. Cross-clamp `level` to `max_levels`.

This model is intentionally boring. It is easy to test, easy to explain
and impossible to crash with a bad value.

## Ghost model

Ghost movement is a small state machine:

- `CHASE`: BFS toward the subclass target.
- `SCATTER`: BFS toward the home corner. Reserved for future scatter
  phases, and used as the frightened retreat target.
- `FRIGHTENED`: BFS toward the corner farthest from Pac-Man at 60
  percent speed. Edible.
- `DEAD_PATHING`: BFS toward the spawn corner at double speed. Not
  edible, not dangerous.
- `DEAD_WAITING`: invisible at the spawn corner for five seconds.
- `FROZEN`: holds the previous state and skips movement. If the
  previous state was frightened, the ghost stays edible.

A frozen ghost keeps a `resume_state`, so a freeze does not silently
turn a frightened ghost into a dangerous one or an eaten ghost into a
live one. This was one of the trickiest edge cases in the project.

## Rendering model

The maze walls are drawn once per level into a cached transparent
surface. Pellets are drawn every frame because they are eaten. Sprites
are loaded once and cached by path, with Pac-Man's open-mouth frames
aligned so the body does not jump. The HUD is drawn every frame. The
last frame without Pac-Man is cached so the death animation can be
played over a stable background.

## Packaging model

`42-pacman.spec` bundles the `resources` directory and the application
code. The build is a one-file executable on Linux and Windows and a
`.app` bundle on macOS. `make package` copies `config.json` and
`README.md` next to the artifact. Packaged runs read the configuration
from the executable directory or the PyInstaller bundle, and store the
database in the platform user-data directory.

## Known limitations

- There is no audio.
- Ghosts do not alternate scatter and chase phases on a timer. They
  chase continuously until frightened or eaten, which keeps the
  behaviour easy to follow.
- The level timer restarts the current level and costs a life when it
  expires. This is a deliberate design choice.
- Highscores are local to the machine, not global.
- The package is prepared for an unlisted itch.io release. The upload is
  a manual team step and is documented in `deployment.md`.
