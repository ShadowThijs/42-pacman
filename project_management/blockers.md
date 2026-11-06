# Blockers

These are the problems that actually slowed the project down. We did not
have any personal conflict. The main issue was scheduling: the two of us
had different course loads, so the ghost phase slipped from August to
October.

## Maze package arrived later than expected

We wanted to start with the loader, but the A-Maze-Ing package was not
available at the beginning. We built the config, state skeleton and
rendering first, then plugged in the 2.0.2 wheel when we had it. The
wheel is now in `maze/`, so a fresh clone can install it.

## Row and column confusion in the maze

The generator gives wall bitmasks but not coordinates. Early collision
code mixed up `(row, col)` and `(x, y)`, which made the reachability
check find only a few tiles. We settled on `maze[row][col]` and
`VECTORS = (column_delta, row_delta)` and fixed the swapped tuple. The
movement tests now protect this.

## Ghost work was split over two periods

tlogtenb wrote the early ghost skeleton in August. asylla wrote the
ghost classes and targets in October, but the collision loop and the
game integration were only finished later. The fix was to give the
ghost files to asylla and keep the game loop changes small. We
pair-programmed the collision, fright and freeze parts.

## Freeze changed what a ghost was

Freezing a frightened ghost could make it dangerous again, and freezing
an eaten ghost could make it edible. We added a `resume_state` to every
ghost. Freeze stores the state underneath, and unfreeze restores it.

## Death and respawn did not line up

Resurrecting Pac-Man immediately hid the death animation. Waiting for
the animation while the game kept running also caused problems. The
final flow detects the life loss, freezes the last frame, runs
`DyingState` on top, and only then respawns and waits for input.

## Score flow did not match the game loop

Saving a score opened the leaderboard instead of returning to the main
menu. We changed both save and skip to reset the stack to the main menu,
and put the top five scores on the menu so the result is still visible.

## `level` was loaded but ignored

This was one of the bugs we already knew about. `Config` read `level`,
but `start_new_game` always set the game to 1. It now uses the
configured level, clamped to `max_levels`, and a test checks it.

## CI lint failed

The macOS and Linux CI jobs failed on a line-length error in
`src/game.py`. We added a `.flake8` config, fixed the line and the
examples, and made CI run `flake8 .` and the same mypy flags as
`make lint`.

## Packaging missed the config and docs

The first package was only the executable. We added `config.json` and
the README to the spec and to the copy step in `make package`, and the
game already has an instructions screen. The Linux smoke test now runs
with the packaged config.

## The itch.io upload needs an account

The package is built and tested, but publishing needs the team's
itch.io account. We wrote the upload steps in `deployment.md`. This is
the only remaining external action.
