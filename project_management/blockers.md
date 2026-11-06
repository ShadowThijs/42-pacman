# Blocking points and conflicts

This document records the points that stopped or slowed the project and
how they were resolved. It is intentionally specific.

## B1. Maze generator package was not available at the start

- **Impact**: the level loader and rendering could not be finished.
- **Resolution**: the team built the configuration loader and the state
  skeleton first, then integrated the 2.0.2 wheel when it was
  available. The wheel is now committed in `maze/`.
- **Lesson**: isolate the generator behind a small call site so the rest
  of the game can be developed with a placeholder.

## B2. Maze bitmask orientation

- **Impact**: early collision and pathfinding code confused rows and
  columns because the generator publishes wall bits but not coordinates.
- **Resolution**: the project standardised on `maze[row][col]` and
  documented that direction vectors are `(column_delta, row_delta)`.
  `models.can_move`, `PacMan` and `Ghost` all use the same convention.
  The reachability test caught one remaining swapped tuple.
- **Status**: resolved and covered by movement tests.

## B3. Ghost interaction was merged late

- **Impact**: the ghosts could chase, but collision, frightened mode and
  eaten-ghost behaviour were not connected to the game loop for a long
  time.
- **Resolution**: asylla implemented the ghost classes, targets and
  frighten state. The team then integrated the collision loop and the
  release schedule. Some of this integration was pair-programmed and is
  recorded in commits under tlogtenb's account.
- **Status**: resolved, covered by ghost tests and manual play.

## B4. Freeze changed the ghost identity

- **Impact**: freezing a frightened ghost could make it dangerous, and
  freezing an eaten ghost could make it edible again.
- **Resolution**: every ghost keeps a `resume_state`. `freeze` stores the
  state beneath the freeze, and `unfreeze` restores it. A frightened
  ghost stays frightened and keeps its timer.
- **Status**: resolved and recorded in `risk_analysis.md` as R11.

## B5. Death animation and respawn timing

- **Impact**: respawning Pac-Man immediately hid the death animation, or
  left input disabled after the animation.
- **Resolution**: gameplay now detects the life loss, freezes the last
  frame, pushes `DyingState`, and calls `reset_death` only after the
  animation. Ghosts wait for the next input before their release
  schedule resumes.
- **Status**: resolved.

## B6. Score flow did not match the required game loop

- **Impact**: the name prompt opened the leaderboard instead of returning
  to the main menu. The intended loop is
  `Main Menu > start game > Win or Lose > Enter name > Back to Main Menu`.
- **Resolution**: `App.submit_score` and `App.skip_score` now reset the
  stack to the main menu. The main menu displays the top five and a
  `SCORE SAVED` notice, so the player still sees the result immediately.
- **Status**: resolved and covered by `test_submitting_score_returns_to_main_menu`.

## B7. Configuration value `level` was loaded but unused

- **Impact**: the game always started at level 1, which is exactly the
  defect reported by the team. It also made the configuration look
  correct while silently ignoring a documented value.
- **Resolution**: `Config.level` is now the starting level, clamped to
  `max_levels`. The first generated maze still uses the fixed seed for
  the session. The HUD shows the configured level and the final level.
- **Status**: resolved and covered by `test_start_uses_configured_level`.

## B8. Lint failures blocked CI

- **Impact**: the macOS and Linux CI jobs failed on a line-length error,
  so the build matrix could not be trusted.
- **Resolution**: the team added `.flake8`, fixed the long lines and
  example annotations, and made `make lint` run `flake8 .` plus the exact
  mypy flags. Both `make lint` and `make lint-strict` now pass.
- **Status**: resolved.

## B9. Packaging missed documents

- **Impact**: the first package was only the executable, with no
  in-package configuration or instructions.
- **Resolution**: `make package` copies `config.json` and `README.md`
  into `dist/`, the spec bundles the resources, and the game has an
  in-game Instructions screen. CI also verifies the bundled resources.
- **Status**: resolved.

## B10. Itch.io publication is an external step

- **Impact**: the repository can prove that the package is
  reproducible, but publishing to a gaming platform needs an account
  and a manual upload.
- **Resolution**: the team prepared the artifacts and a full checklist
  in `deployment.md`. The upload is the only remaining external action.
- **Status**: open by design, to be completed by the team.

## Conflicts

No personal conflict blocked the project. The main coordination
conflict was scheduling: the two students had different course loads,
which is why the ghost phase moved from August to October. The team
resolved it by splitting ownership by file and feature, by keeping the
interfaces small, and by doing a joint integration session before the
final packaging and compliance passes.
