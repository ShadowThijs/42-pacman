# Risk analysis

The register is reviewed at each weekly checkpoint. Probability and
impact are rated low, medium or high. Every risk has an owner and a
mitigation. The status column is the state at the final compliance pass.

| ID | Risk | Probability | Impact | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | Maze generator has a different interface or fails at runtime | Medium | High | Pin the 2.0.2 wheel in `maze/`, call only public API, catch generator exceptions and return to the menu, document the interface. | tlogtenb | Mitigated |
| R2 | Maze generator is reinstalled during peer review and changes behaviour | Medium | High | Keep the exact wheel in the repository and list it in `pyproject.toml`. The loader does not depend on private attributes. | tlogtenb | Mitigated |
| R3 | Malformed configuration crashes the game during review | High | High | Typed defaults, range clamping, comment stripping, unknown-key handling, top-level exception handler, automated config tests. | tlogtenb | Mitigated |
| R4 | A config value is silently ignored, as happened with `level` | High | High | Every documented key is read in `Config` and covered by a test. `level` is now the starting level. | tlogtenb | Fixed |
| R5 | Python traceback reaches the user | Medium | High | `main()` catches all exceptions, config and database code catch expected errors, generator failures are handled. | tlogtenb | Mitigated |
| R6 | Missing or corrupt highscore database | Medium | Medium | SQLite errors are caught, the connection is disabled, the game continues with an empty leaderboard, tests cover a corrupt file. | tlogtenb | Mitigated |
| R7 | Highscore name contains invalid characters or is too long | Medium | Low | Input filter plus database sanitisation plus truncation to ten characters. | tlogtenb | Mitigated |
| R8 | Score decreases or overflows | Low | Medium | Points are clamped to non-negative values, score is only incremented, `int` is unbounded in Python. | tlogtenb | Mitigated |
| R9 | Pac-Man or a ghost crosses a wall | Medium | High | Shared `can_move` rule, movement resolved between tile centres, tests for blocked and open directions. | tlogtenb | Mitigated |
| R10 | Pellet is placed on an unreachable tile, making a level impossible | Medium | High | Pellets are sampled only from the reachable set computed from the player spawn. | tlogtenb | Mitigated |
| R11 | Ghost freeze turns a frightened or eaten ghost into a dangerous one | Medium | High | Ghosts keep a `resume_state`, and tests cover the freeze transition. | asylla and tlogtenb | Mitigated |
| R12 | Death animation and respawn state disagree | Medium | Medium | The last frame is frozen, the animation runs in its own state, and respawn waits for the next input. | tlogtenb | Mitigated |
| R13 | Timer expires during a menu or pause | Low | Medium | The timer is advanced only by the gameplay state, and pauses stop updates. | tlogtenb | Mitigated |
| R14 | Packaging misses resources or the config file | Medium | High | The spec bundles `resources`, `make package` copies config and README, CI verifies the archive and runs a smoke test. | tlogtenb | Mitigated |
| R15 | CI fails on a different operating system | Medium | Medium | Build matrix on Linux, Windows and macOS, plus archive inspection and a headless smoke test. | tlogtenb | Mitigated |
| R16 | flake8 or mypy fails during review | High | High | `.flake8` configuration, exact `make lint` commands, strict typing, CI lint step and a clean local run. | both | Mitigated |
| R17 | Scope creep delays the mandatory features | High | High | Mandatory features first, optional audio and online scores explicitly out of scope. | both | Mitigated |
| R18 | Merge conflicts between the two students | Medium | Medium | Feature ownership, small commits and integration on the shared branch. | both | Mitigated |
| R19 | One student cannot explain the other's code | Medium | High | Pair reviews, contribution table, shared acceptance tests and a walkthrough of each module. | both | Mitigated |
| R20 | AI-generated code is not understood | Medium | High | Every change is reviewed, run and tested. AI is used for suggestions and repetitive work, not as a replacement for understanding. | both | Controlled |
| R21 | The itch.io upload is not ready before release | Medium | High | Build artifacts are reproducible with `make package`, the upload checklist is written, and the team performs the upload. | both | Open, manual step |
| R22 | Frame rate drops on a slower machine | Low | Medium | Cached maze layer, cached sprites, capped delta time, BFS limited to a 20 by 20 maze. | tlogtenb | Mitigated |
| R23 | Window resize breaks the layout | Medium | Low | Logical scaled surface, layout recomputed from the current screen size. | tlogtenb | Mitigated |
| R24 | User closes the window during a game | Low | Low | QUIT is handled, the main loop stops, the database and pygame are closed. | tlogtenb | Mitigated |

## Risk response process

1. A new risk is added to the register when it is identified in a
   checkpoint or a review.
2. The owner proposes a mitigation and, when possible, an automated
   check.
3. The mitigation is verified in the next checkpoint.
4. A risk is closed only when the evidence exists in the repository,
   for example a test name or a CI step.

## Residual risks

- The itch.io page is an external artifact. The repository can prove
  that the package is reproducible, but the upload itself must be done
  by the team.
- A future version of the maze generator could change its public
  interface. The pinned wheel and the adapter-style loader reduce this
  risk, but they cannot eliminate it.
- No automated test can prove that the game feels good. Manual play
  sessions remain part of the acceptance plan.
