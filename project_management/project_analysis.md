# Project analysis

## What we wanted to build

A complete Pac-Man game in Python, using the A-Maze-Ing package for the
maze, pygame for the graphics, a persistent highscore file and a
packaged desktop build. The game had to stay playable when the config
file was wrong, and it had to be easy to demonstrate with cheats.

We also wanted the code to be something we could explain line by line in
review, not a black box built from copy-pasted snippets.

## What we left out

- Sound and music.
- Online highscores. The leaderboard is local.
- Web or mobile builds.
- Reimplementing the maze generator. The package is a dependency.
- Extra game modes beyond the ten-level arcade run.

## Main choices

### pygame

We used pygame because it works on Linux, Windows and macOS, it handles
SVG sprites through SDL_image, and it is the library most people in the
42 Python track already know. The alternative was MLX, which is C
oriented and would have made the project less portable outside the
school machines.

### A state stack

The game has a main menu, a playable screen, a pause overlay, a death
animation, a game over screen, a victory screen and a leaderboard. We
implemented these as states on a stack. The top state receives input and
updates, and the whole stack is drawn from bottom to top. That is why
the pause menu can dim the maze without mutating the game, and why the
death animation can play over a frozen frame.

The alternative was one big loop with mode flags. It starts simple but
gets messy when more than two overlays can appear.

### Flat JSON configuration

We kept the config flat: one key per setting. It is easy to document,
easy to clamp and easy to edit during a demo. The trade-off is that we
cannot override settings per level, but we did not need that.

Every key has a type and a range. A wrong type falls back to the
default, an out-of-range number is clamped, and unknown keys are
ignored. The parser strips `#`, `//` and block comments before handing
the text to `json.loads`.

### SQLite for highscores

A JSON file would have worked, but SQLite gives us ordering and a limit
for free, plus atomic writes and a standard library driver. The table
only has a name and a score. After each insert we delete everything
outside the top ten. If the file is missing or corrupt, the game runs
with an empty board instead of crashing.

### Bitmask maze cells

The A-Maze-Ing package already publishes each cell as a wall bitmask:
north `1`, east `2`, south `4`, west `8`. We use that value for drawing
walls, checking movement and pathfinding. We did not convert it to a
second grid, because that would add a lossy step and another source of
bugs.

### Movement between tile centres

Pac-Man and the ghosts move from centre to centre. A direction press is
queued and resolved at the next centre, so a turn pressed slightly early
is not lost. A reverse press is applied immediately, even mid-tile. The
shared `can_move` helper decides whether a side of a cell has a wall, so
Pac-Man and the ghosts obey the same rule.

### Breadth-first ghost pathfinding

Four ghosts at 60 FPS in a 20 by 20 maze do not need A*. BFS gives a
shortest path and is fast enough. Each ghost subclass only supplies a
target tile. The base class handles turning, wall checks, frightened
state, eaten state and drawing.

We made frightened ghosts run to the corner farthest from Pac-Man. The
first version sent them to their own corner, which looked wrong when the
player was standing near that corner.

### Packaging

`42-pacman.spec` builds a one-file executable on Linux and Windows and a
`.app` bundle on macOS. The spec includes the sprites and font, and we
also copy `config.json` and the README next to the build. CI runs the
same recipe on all three systems.

## How the parts fit together

`pac-man.py` reads the CLI and creates `Config`, `Database` and `Game`.
`App` owns the menu flow and the shared `Theme`. `Game` owns the level,
pellets, Pac-Man, ghosts, score, timer and cheats. `StateManager` owns
the screen stack. `PacMan` and `Ghost` own their movement and animation
but use `models.can_move` for walls. `Database` is the only place with
SQL.

## Things that were harder than expected

- Keeping the ghost state machine correct when freeze, fright and eaten
  states overlap.
- Getting the death animation to play without the game continuing in the
  background.
- Making the first level fully reproducible. The maze seed was easy, but
  the pellet layout used the global random state, so we gave each level
  its own `random.Random`.
- Keeping flake8 and mypy clean while the UI file grew.
- Packaging resources and the config file so the executable works
  outside the repository.

## Known limitations

- No audio.
- Ghosts always chase outside frightened mode. There is no timed
  scatter/chase cycle.
- The timer restarts the level and costs a life when it reaches zero.
- Highscores are local to the machine.
- The packaged build is published on itch.io at
  https://shadowthijs.itch.io/42-pacman.
