# State Architecture

The game runs on a stack of states owned by `StateManager` in
`src/state.py`. `models.py` no longer contains any state handling.

## Stack semantics

- `push(state)` adds an overlay on top of the current screen.
- `pop()` removes the top state.
- `replace(state)` swaps the top state.
- `reset(state)` clears the whole stack and starts again with `state`.
- **Events and updates go to the top state only.** This is what freezes
  gameplay while the pause overlay is open.
- **Drawing walks the whole stack bottom to top.** Full-screen states paint
  their own background; overlays (pause) dim the frozen screen underneath.

## Files

```
src/
  state.py            State base class + StateManager
  game.py             Game session, gameplay update, main loop
  ui/
    app.py            Screen flow (start -> game -> death -> scores)
    theme.py          Arcade fonts, colours, text helpers
    components.py     Text-only menu item with mouse + keyboard focus
    screens.py        Start, game, pause, death, name entry, leaderboard
```

## Screen flow

```
StartMenu
  PUSH ENTER TO START -> GameScreen
  LEADERBOARD         -> LeaderboardScreen
  QUIT                -> exit

GameScreen
  arrows / WASD       -> move
  P / ESC             -> PauseMenu (overlay)
  Q                   -> exit
  life lost           -> DyingState -> GameScreen (READY!)
  last life lost      -> DyingState -> NameEntry

NameEntry
  ENTER               -> save score -> Leaderboard
  ESC                 -> skip -> Leaderboard

Leaderboard
  PLAY AGAIN          -> GameScreen
  MAIN MENU           -> StartMenu
```

## Gameplay integration

`Game` still owns the original gameplay update:

- `Game.update(dt)` contains the original Pac-Man/ghost update, score,
  collision and level-clear logic. Input handling was moved to
  `GameScreen`, not changed in `player.py` or `ghost.py`.
- `Game.die()` now sets `game_over` instead of stopping the application,
  so the state stack can show the death and name-entry screens.
- `Game.run()` is the state-driven main loop and always leaves through
  `pygame.quit()`.
- `player.py`, `ghost.py` and `sprites.py` are untouched.

## Arcade layout

The window is derived from the maze size in `pac-man.py`:

```
width  = config.width  * CELL_SIZE + 100
height = config.height * CELL_SIZE + 80
```

For the default 20x20 maze that is 820x800. The maze stays at
`OFFSET = (50, 50)`, leaving one classic HUD line above it and one lives
line below it:

- top: `1UP` + score, `HIGH SCORE` + score, `LEVEL` + level
- bottom: remaining Pac-Man lives
- center: `READY!` before the first input / after a respawn

Everything uses the ArcadeClassic pixel font when available, with
ByteBounce or a mono font as fallback.

## Scores

- `db_init()` creates the SQLite database configured by `highscore_db`.
- `Game.leaderboard()` reads the top scores through `db.py`.
- `Game.record_score()` writes a score through `db.py`.
- The leaderboard screen renders the top ten (empty slots included) and
  highlights the newly saved row.
