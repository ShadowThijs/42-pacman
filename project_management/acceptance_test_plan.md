# Acceptance test plan

This document maps every project requirement to concrete evidence.
Automated checks are preferred. Manual steps are written so a reviewer
can reproduce them during a review.

## How to run the automated checks

```sh
make install
make lint
make lint-strict
make test
```

Expected result: flake8 reports nothing, mypy reports no issues, and all
38 tests pass.

The tests force SDL's dummy video and audio drivers, so they run without
a desktop session. They create temporary config and SQLite files and do
not touch the repository database.

## Automated test inventory

| Test | Requirement covered |
| --- | --- |
| `test_clean_json_removes_all_supported_comments` | `#`, `//` and `/* */` comments |
| `test_clean_json_keeps_comment_markers_inside_strings` | Comment markers inside strings are preserved |
| `test_sanitize_name_uppercases_and_filters` | Name is uppercased, invalid characters removed |
| `test_sanitize_name_truncates_to_ten_characters` | Maximum name length |
| `test_config_defaults_when_file_is_missing` | Missing file uses defaults |
| `test_config_uses_configured_level` | `level` controls the starting level |
| `test_config_level_is_clamped_to_max_levels` | `level` is clamped to `max_levels` |
| `test_config_invalid_types_and_values_are_safe` | Wrong types and out-of-range numbers |
| `test_config_unknown_keys_are_ignored` | Unknown keys are ignored |
| `test_config_invalid_json_uses_defaults` | Invalid JSON does not crash |
| `test_config_root_must_be_an_object` | Non-object JSON root is rejected safely |
| `test_database_persists_scores_across_connections` | Highscores persist on disk |
| `test_database_keeps_only_top_ten` | Top-ten limit and pruning |
| `test_database_sanitizes_names_and_scores` | Name and score rules at the database layer |
| `test_database_handles_corrupt_file` | Corrupt database is tolerated |
| `test_db_init_creates_configured_database` | Configured database path is created |
| `test_db_init_handles_unwritable_path` | Unwritable path is tolerated |
| `test_start_uses_configured_level` | Starting level in the game session |
| `test_first_level_is_deterministic` | Fixed seed produces the same first level |
| `test_initial_level_contents` | Pellets, four power pellets, four ghosts, lives |
| `test_eating_pacgum_increases_score` | Normal pellet scoring |
| `test_player_cannot_cross_walls` | Wall collision |
| `test_player_moves_through_open_corridor` | Movement through corridors |
| `test_eating_supergum_increases_score` | Power pellet scoring |
| `test_frightened_ghost_becomes_edible` | Frightened state and expiry |
| `test_frightened_ghost_flees_to_far_corner` | Frightened ghosts move away from Pac-Man |
| `test_eating_frightened_ghost_scores` | Eating an edible ghost |
| `test_eaten_ghost_respawns` | Eyes return and ghost resumes chasing |
| `test_level_advance_keeps_score_and_lives` | Score and lives carry between levels |
| `test_victory_after_final_level` | Victory after the last level |
| `test_timer_expiry_costs_a_life` | Level timer expiry costs a life |
| `test_timer_expiry_on_last_life_ends_game` | Timer expiry on last life ends the game |
| `test_invincible_cheat_prevents_timer_death` | Invincibility cheat |
| `test_cheat_keys_enable_and_apply` | In-game cheat hotkeys and extra lives |
| `test_ui_screens_render` | Main menu, instructions, game, pause, victory and name entry |
| `test_submitting_score_returns_to_main_menu` | Save score and return to the main menu |
| `test_name_entry_limits_length` | Name entry maximum length |
| `test_cheats_class_toggles` | Cheat flags toggle independently |

## Requirements checklist

### Preliminaries and files

| Requirement | Evidence | Status |
| --- | --- | --- |
| Work is in the git repository | All source, docs, tests, spec and wheel are tracked | Pass |
| Required files are present | `README.md`, `Makefile`, `pac-man.py`, `config.json`, `42-pacman.spec`, `src/`, `project_management/` | Pass |

### Project management

| Requirement | Evidence | Status |
| --- | --- | --- |
| Dedicated project management subdirectory | `project_management/` with overview, timeline, analysis, risks, roles, progress, acceptance plan, blockers and deployment | Pass |
| One-minute tour | `project_management/README.md` | Pass |
| Clear view of management and organization | `team_organization.md`, `timeline.md`, `progress_tracking.md` | Pass |

### README

| Requirement | Evidence | Status |
| --- | --- | --- |
| Present at repository root | `README.md` | Pass |
| Italic first line with both logins | First line names tlogtenb and asylla | Pass |
| Description section | `## Description` | Pass |
| Instructions section | `## Instructions` with install, run, CLI and Makefile rules | Pass |
| Resources section and AI usage | `## Resources` with classic references and AI usage | Pass |
| Configuration section | `## Configuration` with every key, default, range and example | Pass |
| Highscore section | `## Highscore` with storage, rules and rationale | Pass |
| Maze Generation section | `## Maze Generation` with package version and interface | Pass |
| Implementation section | `## Implementation` | Pass |
| General Software Architecture section | `## General Software Architecture` with tree and diagram | Pass |
| Project Management section | `## Project Management` with directory link | Pass |

### Makefile

| Requirement | Evidence | Status |
| --- | --- | --- |
| `install` rule | `make install`, uv or pip fallback | Pass |
| `run` rule | `make run` calls `pac-man.py config.json` | Pass |
| `debug` rule | `make debug` runs `pdb -c continue` | Pass |
| `clean` rule | Removes caches and build artifacts | Pass |
| `lint` rule | `flake8 .` and mypy with the requested flags | Pass |
| `lint-strict` rule | `flake8 .` and `mypy . --strict` | Pass |
| No required rule missing | All mandatory rules present | Pass |

### Code quality

| Requirement | Evidence | Status |
| --- | --- | --- |
| flake8 has no errors or warnings | `make lint` exits 0 | Pass |
| mypy has no errors or warnings | `make lint` and `make lint-strict` exit 0 | Pass |
| Type hints and docstrings | All functions and classes are annotated and documented | Pass |
| Exceptions handled without traceback | `pac-man.py` top-level handler, config and database guards, generator guard | Pass |

### Usage and CLI

| Requirement | Evidence | Status |
| --- | --- | --- |
| Exactly one argument, a JSON config | `python3 pac-man.py config.json` runs, zero or two arguments print usage and exit 1 | Pass |
| Missing or wrong arguments handled clearly | Manual: `python3 pac-man.py` prints `Error: missing configuration file.` and the usage line | Pass |
| Too many arguments handled clearly | Manual: `python3 pac-man.py config.json extra` prints `Error: too many arguments.` | Pass |
| `run` rule follows expected usage | `make -n run` shows `pac-man.py config.json` | Pass |
| No traceback for a missing file | Manual: `python3 pac-man.py /tmp/nope.json` logs a warning and starts with defaults | Pass |

### Configuration

| Requirement | Evidence | Status |
| --- | --- | --- |
| JSON format | Standard JSON parser, comment stripper | Pass |
| Comments handled | `#`, `//`, `/* */`, tests | Pass |
| Defaults and clamping | `Config._validated`, config tests | Pass |
| Unknown keys ignored | Config test and clear log line | Pass |
| All values actually used | `level`, `width`, `height`, `lives`, `pacgum`, points, `seed`, time, `max_levels`, DB path are all read by the game | Pass |
| Defensive edit test | Change `level` to 4, run, HUD shows `LEVEL 04 OF 10` | Pass |

### Error handling

| Requirement | Evidence | Status |
| --- | --- | --- |
| Clear messages, no traceback | Config, database and generator paths print messages, top-level handler catches the rest | Pass |
| Crash flag avoided | Headless fuzz run and full test suite complete without unhandled exceptions | Pass |

### Build and run

| Requirement | Evidence | Status |
| --- | --- | --- |
| `make install` works | uv path and pip fallback are implemented | Pass |
| `make run` works | Starts the game with `config.json` | Pass |
| Packaged build works | `make package`, then a headless smoke test of `dist/42-pacman` | Pass |

### Main menu

| Requirement | Evidence | Status |
| --- | --- | --- |
| Start a new game | `START GAME` item | Pass |
| Highscore view | `VIEW HIGHSCORES` item and top-five panel | Pass |
| Instructions with controls and rules | `INSTRUCTIONS` screen | Pass |
| Quit | `EXIT` item | Pass |

### Level structure

| Requirement | Evidence | Status |
| --- | --- | --- |
| First level always the same | `test_first_level_is_deterministic`, configured seed | Pass |
| Corridors, walls, pellets, power pellets, player and ghosts | `test_initial_level_contents`, manual play | Pass |
| Player starts in the middle | `_select_spawn_tile` chooses the walkable tile nearest the centre | Pass |
| Four ghosts, one per corner | `spawn_ghosts`, initial level test | Pass |

### Player mechanics

| Requirement | Evidence | Status |
| --- | --- | --- |
| Can move in the maze | `test_player_moves_through_open_corridor` | Pass |
| Cannot cross walls | `test_player_cannot_cross_walls` | Pass |
| Can eat pacgums and super-pacgums | Scoring tests | Pass |
| Can die and respawn | Timer death test, manual ghost collision, `DyingState` and `reset_death` | Pass |
| Starts with three lives by default | Config default and initial level test | Pass |

### Ghost mechanics

| Requirement | Evidence | Status |
| --- | --- | --- |
| Autonomously chase | BFS chase logic in `ghost.py`, manual play | Pass |
| Flee when edible | Frightened state targets the corner farthest from Pac-Man, manual play | Pass |
| Can be eaten | `test_eating_frightened_ghost_scores` | Pass |
| Respawn after a while | `test_eaten_ghost_respawns`, five-second delay | Pass |

### Pacgums and super-pacgums

| Requirement | Evidence | Status |
| --- | --- | --- |
| Pacgums present and edible | `test_initial_level_contents`, `test_eating_pacgum_increases_score` | Pass |
| Super-pacgums present and edible | Four corners, `test_eating_supergum_increases_score` | Pass |
| Score increases appropriately | Points are read from config in `Game.update` | Pass |
| Ghosts flee for a limited time | `frighten`, seven-second timer, speed reduction | Pass |

### Scoring

| Requirement | Evidence | Status |
| --- | --- | --- |
| Score displayed during the game | `GameScreen._draw_top_hud` | Pass |
| Score increases for pellets, power pellets and ghosts | Scoring tests and manual play | Pass |
| Score never decreases | Points clamped non-negative, score only incremented | Pass |

### Cheat mode

| Requirement | Evidence | Status |
| --- | --- | --- |
| Invincibility | Key `1`, timer and ghost damage prevention | Pass |
| Level skip | Key `5` | Pass |
| Ghost freeze | Key `3` | Pass |
| Extra lives | Key `4`, repeatable | Pass |
| Increased speed | Key `2` | Pass |
| Easy to demonstrate | Konami unlock plus hotkeys that also activate the mode, HUD labels and instructions screen | Pass |

### Game progression

| Requirement | Evidence | Status |
| --- | --- | --- |
| Full cycle from new game to game over | `test_ui_screens_render`, manual full-cycle script below | Pass |
| Win or lose a level | Level advance and victory tests | Pass |
| Add a name to the highscore board | `test_submitting_score_returns_to_main_menu`, name entry test | Pass |
| Pause and resume | Pause state test | Pass |
| Timer limit | Timer tests | Pass |
| Score and lives carry between levels | `test_level_advance_keeps_score_and_lives` | Pass |
| Game ends after all levels or all lives | Victory and game-over tests | Pass |
| Return to the main menu after the game | Submit and skip both call `show_start_menu` | Pass |

### Highscore persistence

| Requirement | Evidence | Status |
| --- | --- | --- |
| Persistent storage | SQLite file, reopen test | Pass |
| Robust to file errors | Corrupt and unwritable tests | Pass |
| Names max 10, alphanumeric and spaces | UI filter, `sanitize_name`, tests | Pass |
| Scores non-negative integers | Database sanitisation and test | Pass |
| Top ten with names and scores | Pruning test, leaderboard screen | Pass |
| Loaded at start, saved at end | `best_score`, name entry, database tests | Pass |
| Player can enter a name on win or lose | `NameEntryScreen` and `VictoryScreen` | Pass |
| Displayed in the main menu | Highscore line and top-five panel | Pass |

### User interface

| Requirement | Evidence | Status |
| --- | --- | --- |
| Main menu has all required elements | Start, highscores, instructions, exit | Pass |
| In-game HUD has score, lives, level, time | `_draw_top_hud` and `_draw_bottom_hud` | Pass |
| Pause menu has resume and main menu | `PauseMenuScreen` | Pass |
| Game over screen has final score and name prompt | `NameEntryScreen` | Pass |
| Victory screen has final score, message and name prompt | `VictoryScreen` | Pass |

### Maze generator integration

| Requirement | Evidence | Status |
| --- | --- | --- |
| Maze package is used | `from mazegenerator import MazeGenerator` in `src/game.py` | Pass |
| Package is not altered | Wheel is committed unchanged, no vendored copy | Pass |
| Reinstall works | `uv sync` or `pip install maze/mazegenerator-2.0.2-py3-none-any.whl` | Pass |
| Package is not discarded | Every level is built by `MazeGenerator`, tests compare generated mazes | Pass |
| `PERFECT` is `False` | Second positional argument is `False` | Pass |
| Generator failure handled | `try/except` around construction and empty-maze check | Pass |

### Object-oriented programming

| Requirement | Evidence | Status |
| --- | --- | --- |
| Classes for each logic element | `Game`, `PacMan`, `Ghost` and four subclasses, `Config`, `Database`, `Cheats`, `Sprites`, `State`, screens, `Theme`, `Button` | Pass |
| Shared wall rule | `models.can_move` is used by Pac-Man and ghosts | Pass |
| Inheritance used sensibly | `Ghost` base class with `Blinky`, `Pinky`, `Inky`, `Clyde`; `MenuScreen` and state subclasses | Pass |

### Packaging and deployment

| Requirement | Evidence | Status |
| --- | --- | --- |
| Package can be regenerated live | `make package` with the root spec | Pass |
| Package is fully functional | Headless smoke test of the built executable | Pass |
| Minimal in-package instructions | In-game Instructions screen, bundled README and config | Pass |
| Full source and packaging script in the repository | `src/`, `42-pacman.spec`, CI workflow | Pass |
| Public build on a gaming platform | Artifacts are ready, upload is the team's manual step | Pending upload |

## Manual full-cycle script

Use this script during a review.

1. `make install`
2. `make run`
3. Confirm the main menu shows start, highscores, instructions and exit.
4. Open `INSTRUCTIONS` and confirm the controls, rules and cheat keys.
5. Return to the menu, enter the Konami code, confirm the rainbow title
   and `CHEATS ACTIVE`.
6. Start a game. Confirm the HUD shows score, level, lives and time.
7. Press `P`, confirm the pause menu, choose `RESUME`.
8. Eat a pacgum and confirm the score increases by `pp_pacgum`.
9. Eat a super-pacgum and confirm the score increases by
   `pp_super_pacgum` and ghosts turn blue and flee.
10. Eat a blue ghost and confirm the score increases by `pp_ghost` and
    the eyes return to the corner.
11. Press `3` to freeze the ghosts, walk through one and confirm no life
    is lost while the ghost is not edible.
12. Press `3` again to release the ghosts.
13. Press `1` for invincibility, let a ghost touch Pac-Man and confirm no
    life is lost.
14. Press `5` to skip a level and confirm the level number increases.
15. Press `4` several times and confirm the lives increase.
16. Let the timer run out, or let a ghost catch Pac-Man with the cheats
    off, and confirm a life is lost and Pac-Man respawns in the middle.
17. Lose the last life. Confirm the game-over screen shows the final
    score and asks for a name.
18. Enter a name, press Enter and confirm the main menu appears with the
    saved score and the new entry in the top-five panel.
19. Open `VIEW HIGHSCORES` and confirm the name and score are in the top
    ten.
20. Quit the game, run `make run` again and confirm the score is still
    in the leaderboard.
21. Change `level` to `4` in `config.json`, restart and confirm the HUD
    shows level 4.
22. Change a value to an invalid type, restart and confirm the warning
    and the default value.
23. Remove a key, restart and confirm the default is used.
24. Add an unknown key, restart and confirm it is ignored.
25. Use `5` repeatedly to reach the final level and win. Confirm the
    victory screen shows the score, the congratulation message and the
    name prompt.
26. Enter a name, confirm the main menu and the saved score.

## Defensive configuration tests

| Edit | Expected result |
| --- | --- |
| Delete `config.json` argument | Usage message, exit code 1 |
| Pass two arguments | Usage message, exit code 1 |
| Pass a nonexistent path | Warning, defaults, game starts |
| Write invalid JSON | Warning, defaults, game starts |
| Set `lives` to `true` | Warning, default 3 used |
| Set `width` to 999 | Warning, clamped to 50 |
| Set `pacgum` to -1 | Warning, clamped to 0 |
| Set `level` to 99 | Warning, clamped to `max_levels` |
| Set `seed` to 0 | Warning, clamped to 1 |
| Set `pp_ghost` to -50 | Warning, clamped to 0 |
| Set `highscore_db` to a directory | Database disabled, game continues |
| Add `unknown_key` | Ignored with a log line |
| Use `#`, `//` and block comments | Parsed normally |

## Bugs found and fixed

| Bug | Symptom | Fix | Regression test |
| --- | --- | --- | --- |
| `config.level` ignored | Every new game started at level 1 | `start_new_game` uses `config.level`, clamped to `max_levels` | `test_start_uses_configured_level` |
| Pellets on unreachable tiles | A level could not be completed | Sample only from the reachable set from the player spawn | Reachability is part of level generation and covered by the level tests |
| Missing Instructions screen | Main menu had no instructions entry | Added `InstructionsScreen` and menu item | `test_ui_screens_render` |
| Extra-life cheat capped at 3 | Pressing `4` at the start did nothing | Add a life up to the safe maximum, repeatable | `test_cheat_keys_enable_and_apply` |
| Score saved then leaderboard shown | Required loop ends at the main menu | `submit_score` and `skip_score` return to the main menu | `test_submitting_score_returns_to_main_menu` |
| Main menu did not list scores | Only the single best score was visible | Top-five panel and highscores view | `test_ui_screens_render` |
| `level_max_time` was briefly 90 | Full clears were impractical at the game's movement speed | Restored the 300-second default after playtesting | Config defaults test and manual timing |
| Boolean accepted as an integer | `lives: true` was treated as 1 | Reject bool before integer validation | `test_config_invalid_types_and_values_are_safe` |
| Database connection never closed | Resource left open until process exit | `Database.close`, called from `Game.run` | Database tests |
| Corrupt database printed the exception class | Unhelpful message | Catch and print the actual error, disable storage | `test_database_handles_corrupt_file` |
| Ghost freeze could change identity | Freezing a frightened ghost could make it dangerous | Keep `resume_state` and restore it | Ghost state tests |
| First level pellet layout varied | Level was not fully reproducible | Dedicated `random.Random` seeded per level | `test_first_level_is_deterministic` |
