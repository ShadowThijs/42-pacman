# Risk analysis

We kept a short risk list and updated it when something actually became
a problem. The table is written from the perspective of the finished
project: it lists the risks we worried about, what we did, and how it
ended.

| Risk | How likely it felt | What we did | Status |
| --- | --- | --- | --- |
| The maze package was not available when we started the loader | High | Built the config, state and rendering skeleton first, then used the 2.0.2 wheel once it was available | Closed |
| A reinstalled maze package could behave differently | Medium | Pinned the wheel in `maze/`, used only the public `MazeGenerator` API and the public `maze` property | Closed |
| A bad config file could crash the game | High | Typed defaults, range clamping, comment stripping, unknown-key handling and a top-level exception handler | Closed |
| A config value could be read but never used | High | Each key has a test, and the `level` bug was found and fixed in the final pass | Closed |
| A traceback could appear during review | Medium | Caught expected errors in config, database and maze code, and wrapped the entry point | Closed |
| A missing or corrupt highscore file could stop the game | Medium | Disabled the database cleanly and continued with an empty leaderboard | Closed |
| A name could be too long or contain invalid characters | Medium | Filtered input in the screen and sanitised again in the database | Closed |
| Pac-Man or a ghost could cross a wall | Medium | Shared `can_move` rule, movement between tile centres and wall tests | Closed |
| A pellet could be placed somewhere unreachable | Medium | Sample pellets only from the reachable set computed from the player spawn | Closed |
| Freezing a ghost could change what it really is | Medium | Kept a `resume_state` and restored it on unfreeze | Closed |
| Death and respawn could get out of sync | Medium | Froze the last frame, played the death animation in its own state and resumed only after it | Closed |
| CI could fail on a different operating system | Medium | Build matrix on Linux, Windows and macOS, plus a headless smoke test | Closed |
| flake8 or mypy could fail during review | High | Added `.flake8`, fixed the long lines and made CI run the same commands as `make lint` | Closed |
| The package could miss resources or the config file | Medium | Bundled `resources`, copied `config.json` and the README, checked the archive in CI | Closed |
| We could run out of time on the ghost work | High | Split ghost ownership, integrated in October and tested on the real maze | Closed, but late |
| AI suggestions could end up in code we cannot explain | Medium | Read, ran and tested every suggestion, and rewrote several of them | Controlled |
| The itch.io upload needs the team account | High | Prepared the package and wrote the upload checklist | Open, external step |

## What we would watch next time

- Start the ghost integration earlier, even with a simple maze, so the
  collision and state problems appear before the last month.
- Add the project management folder from the first week. Reconstructing
  the timeline at the end is more work than writing it as we go.
- Run `make lint` and `make test` in CI from the first packaging commit.
  We only found the CI line-length failure late.
- Keep the configuration defaults and the example config in sync. The
  level time changed in two places and that caused confusion.
