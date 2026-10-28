# TODO

- Ghost AIs
- Ghost spawn locations (inside the 4 or 2)
    - Slowly released
    - Blinky (red), starts outside first
- Pacman interaction with ghosts
- Pacman respawning after death
  - Eaten pacgums are still "eaten"
  - Ghosts reset back to spawn
  - Pacman loses 1 life
- Super Gums (allow pacman to eat ghosts)
  - Ghosts becoming vulnerable
  - Ghosts turn to eyes
  - Ghosts navigate to scatter
  - Ghosts slow down in vulnerable state
- Dead ghosts go as eyes back to their spawn position
  - Dead ghosts are no longer vulnerable after respawning.

## Review notes (2026-10-26, not implemented)

### Gameplay / correctness

- **Danger states:** collisions currently kill Pac-Man regardless of ghost
  state. Skip `FRIGHTENED`, `DEAD_PATHING`, and `DEAD_WAITING` ghosts; add
  eat-ghost handling (`pp_ghost`) and call `Ghost.die()`.
- **Dead-ghost target:** `Game.run` overwrites `ghost.target` every frame,
  including during `DEAD_PATHING`, so the spawn target set by `Ghost.die()`
  is lost. Only recompute targets for chase/scatter ghosts.
- **Blinky identity:** `ghosts[0]` is assumed to be Blinky. Look the ghost up
  by type instead, since list order can change.
- **Scatter never happens:** every frame assigns a chase target, so
  `GhostState.SCATTER`, the corner targets, and the state timer are unused.
  Add scatter/chase phase timers.
- **Spawn tiles can be walls:** `_spawn_tile()` returns a literal grid corner.
  Snap each ghost to the nearest open tile, or define a proper ghost house.
- **Spawn search robustness:** `_player_spawn()` uses the config's width and
  height instead of the real maze size and can raise `StopIteration`. Validate
  the chosen tile and use the actual maze dimensions.
- **Death presentation:** DONE. A short `DyingState` animation plays before
  respawn, and `READY!` is shown until the next direction input.
- **HUD / progression:** DONE for score, high score, level and lives. The
  `level_max_time` timer is still unused.
- **Highscores:** DONE. Scores are saved after game over and the leaderboard
  screen reads the top ten through `db.py`.

### Architecture / maintainability

- **Duplicated helpers:** `VECTORS`, `REVERSE`, `SWITCH_DT`, and `_open()` are
  duplicated in `player.py` and `ghost.py`. Move them to `models.py` or a
  shared `movement.py`.
- **Dead state system:** DONE. `Game.run` now drives `StateManager`; menus,
  pause, death and name entry are real states.
- **Quit flow:** DONE. `Game.run` has one `running = False` path and closes
  pygame in `finally`.
- **Init-time attributes:** `Game.__init__` leaves many attributes
  annotation-only until `init_game()`. Pass width/height/config into the
  constructor or give them safe defaults.
- **Seed handling:** `new_level()` mutates `cfg.seed` with `random.randint`
  when `start_level` is true, and the flag name is unclear. Keep the chosen
  seed separately and make level creation explicit.
- **Config validation:** `isinstance(value, type(default))` rejects `2` for a
  float and accepts booleans for ints. Also `config.json` has `"level": ""`.
  Use per-field casts/validators and logging instead of `print`.
- **Pacgum storage:** `list[tuple[int, int]]` plus `list.remove()` and a full
  scan each frame. Use a set/dict keyed by tile for O(1) lookup.
- **Rendering:** sprites are never converted to the display format. Call
  `convert_alpha()` after the display exists and use `get_rect(center=...)`
  instead of hardcoded 16 px offsets.
- **Tests/tooling:** there is no test suite; `make test` references an
  undefined `$(MOD_CMD)`, and `make debug` uses `ipdb`, which is not a
  declared dependency. Add pytest coverage for release timing, respawn,
  movement, and BFS.

### Performance (minor at 20x20)

- BFS runs for every ghost at every tile centre. A single BFS flow field from
  Pac-Man, recomputed on tile changes, would scale better.
- Maze walls are redrawn line by line every frame. Cache the maze to a
  background `Surface` and blit it each frame.
