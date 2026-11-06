# Testing and acceptance

We tested on three levels: the pytest suite for logic, a manual play
script for the parts that need eyes and hands, and a config abuse test
for the error paths.

## Automated tests

Run them with:

```sh
make test
```

The suite is headless. `tests/conftest.py` sets SDL's dummy video and
audio drivers, and each test uses temporary config and database files.
At the end of the project all 38 tests pass.

| Area | Tests | What they cover |
| --- | --- | --- |
| Config text | `test_clean_json_removes_all_supported_comments`, `test_clean_json_keeps_comment_markers_inside_strings` | `#`, `//` and block comments, including markers inside strings |
| Config values | `test_config_defaults_when_file_is_missing`, `test_config_uses_configured_level`, `test_config_level_is_clamped_to_max_levels`, `test_config_invalid_types_and_values_are_safe`, `test_config_unknown_keys_are_ignored`, `test_config_invalid_json_uses_defaults`, `test_config_root_must_be_an_object` | Defaults, the starting level, clamping, wrong types, unknown keys and broken JSON |
| Names | `test_sanitize_name_uppercases_and_filters`, `test_sanitize_name_truncates_to_ten_characters` | Uppercasing, invalid characters and the ten-character limit |
| Database | `test_database_persists_scores_across_connections`, `test_database_keeps_only_top_ten`, `test_database_sanitizes_names_and_scores`, `test_database_handles_corrupt_file`, `test_db_init_creates_configured_database`, `test_db_init_handles_unwritable_path` | Persistence, top ten, sanitising, corruption and bad paths |
| Level start | `test_start_uses_configured_level`, `test_first_level_is_deterministic`, `test_initial_level_contents` | Starting level, fixed seed, pellets, power pellets, ghosts and lives |
| Movement | `test_player_cannot_cross_walls`, `test_player_moves_through_open_corridor` | Wall collision and normal corridor movement |
| Pellets | `test_eating_pacgum_increases_score`, `test_eating_supergum_increases_score` | Pellet scoring |
| Ghosts | `test_frightened_ghost_becomes_edible`, `test_frightened_ghost_flees_to_far_corner`, `test_eating_frightened_ghost_scores`, `test_eaten_ghost_respawns` | Frightened state, retreat target, eating and respawn |
| Progression | `test_level_advance_keeps_score_and_lives`, `test_victory_after_final_level` | Level advance, score and lives carried, victory |
| Timer | `test_timer_expiry_costs_a_life`, `test_timer_expiry_on_last_life_ends_game`, `test_invincible_cheat_prevents_timer_death` | Life loss, game over and invincibility |
| Cheats | `test_cheat_keys_enable_and_apply`, `test_cheats_class_toggles` | Hotkeys, extra lives and cheat toggles |
| UI flow | `test_ui_screens_render`, `test_submitting_score_returns_to_main_menu`, `test_name_entry_limits_length` | Every screen, score return flow and name entry limit |

## Manual play script

Use this after `make run` or with the packaged build.

1. Check that the main menu shows start, highscores, instructions and
   exit.
2. Open the instructions screen and read the controls and cheat list.
3. Return to the menu and enter the Konami code. The title should turn
   rainbow and `CHEATS ACTIVE` should appear.
4. Start a game. Check the HUD for score, high score, level, time and
   lives.
5. Press `P`, check the pause menu, then resume.
6. Eat a pacgum and check the score goes up by 10.
7. Eat a corner power pellet and check the score goes up by 50 and the
   ghosts turn blue.
8. Eat a blue ghost and check the score goes up by 200. The eyes should
   return to the corner and the ghost should come back after about five
   seconds.
9. Press `3` and walk through a ghost. It should not take a life while
   frozen and not edible. Press `3` again to release it.
10. Press `1` and let a ghost touch Pac-Man. No life should be lost.
11. Press `5` to skip a level. The level number should change.
12. Press `4` a few times. The lives should increase.
13. Let the timer run out, or let a ghost catch Pac-Man with cheats off.
    Pac-Man should lose a life and respawn in the middle.
14. Lose the last life. The game over screen should show the score and
    ask for a name.
15. Enter a name and press Enter. The main menu should appear with a
    saved-score message and the new entry in the top scores.
16. Open the highscores screen and check the full top ten.
17. Quit the game, start it again and check that the score is still
    there.
18. Use `5` to reach the last level and win. The victory screen should
    show the score, the message and the name prompt.
19. Enter a name and check that you return to the main menu.

## Config abuse test

| Change | Expected result |
| --- | --- |
| Run with no argument | Usage message, exit code 1 |
| Run with two arguments | Usage message, exit code 1 |
| Pass a missing path | Warning and defaults, game starts |
| Pass invalid JSON | Warning and defaults, game starts |
| Pass a JSON array | Warning and defaults, game starts |
| Set `lives` to `true` | Warning, default 3 |
| Set `width` to 999 | Warning, clamped to 50 |
| Set `height` to -4 | Warning, clamped to 5 |
| Set `pacgum` to -1 | Warning, clamped to 0 |
| Set `level` to 99 | Warning, clamped to `max_levels` |
| Set `level_max_time` to 0 | Warning, clamped to 1 |
| Set `seed` to 0 | Warning, clamped to 1 |
| Set `pp_ghost` to -50 | Warning, clamped to 0 |
| Point `highscore_db` at a directory | Database disabled, game continues |
| Add an unknown key | Ignored with a log line |
| Use all three comment styles | Parsed normally |

We ran this list against the game with SDL's dummy driver and checked
that no run printed a traceback.

## Bugs found and fixed

| Bug | What we saw | Fix |
| --- | --- | --- |
| `level` was ignored | Every new game started at level 1 even when the config said otherwise | `start_new_game` now uses `config.level`, clamped to `max_levels` |
| Pellets could be unreachable | A level could have a pellet behind a wall, so it could not be finished | Pellets are sampled only from the tiles reachable from the spawn |
| No instructions screen | The main menu had no way to read the controls | Added `InstructionsScreen` and a menu entry |
| Extra lives stopped at three | Pressing `4` at the start did nothing | Added one life per press up to the safe maximum |
| Score flow | Saving a score opened the leaderboard instead of the main menu | `submit_score` and `skip_score` return to the main menu |
| Main menu showed one score | The top scores were hidden behind a submenu | Added a top-five panel to the main menu |
| Level time reset | The tuned 300-second default was changed back to 90 during a cleanup pass. 90 seconds is too short for a full maze, even with speed and invincibility | Changed the default back to 300 and updated the example config |
| Boolean config values | `lives: true` was accepted as 1 | Reject bool before integer validation |
| Database left open | The SQLite connection was only closed when the process ended | Added `Database.close` and call it on game exit and startup failure |
| Corrupt database message | The error message printed the exception class, not the error | Catch and print the real error, then disable storage |
| Freeze changed a ghost | Freezing a frightened ghost could make it dangerous | Keep `resume_state` and restore it on unfreeze |
| First level varied | Pellet layout used the global random state | Give each level its own `random.Random` seeded from the level seed |

## What still needs a person

The tests cannot tell us whether the game feels right. The manual script
above is the part we run before a release. It covers the menu flow,
cheat demonstration, ghost behaviour, scoring, the timer, the name
entry, persistence and the victory screen.
