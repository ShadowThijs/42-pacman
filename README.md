# 42-pacman

https://www.sqlitetutorial.net/sqlite-order-by/
https://dev.to/lovelacecoding/how-to-build-your-first-python-game-a-step-by-step-guide-to-creating-a-simple-shooter-with-pygame-f0k

## Packaging

Build a local one-file executable with PyInstaller:

```sh
make package
# or
uv run pyinstaller --clean --noconfirm 42-pacman.spec
```

The output is written to `dist/`. Linux and Windows produce a single
executable. macOS produces a `.app` bundle, which the CI workflow packages
as a DMG.

The GitHub Actions workflow in `.github/workflows/build.yml` builds
Linux (Ubuntu 22.04), Windows and macOS artifacts. It runs on a push to
`master`/`main`, on a `v*` tag, or manually through the Actions tab.
GitHub wraps workflow artifacts in a zip automatically, so the downloaded
artifact only needs to be extracted once. On Linux, restore the executable
bit with `chmod +x 42-pacman` if your extractor drops it.

Packaged builds use the settings baked into the application. To override
them, place a `config.json` next to the executable. Highscores stay in the
current directory when running from source. Packaged builds store the
database in the platform user-data directory:

- Linux: `$XDG_DATA_HOME/42-pacman/` or `~/.local/share/42-pacman/`
- Windows: `%APPDATA%\42-pacman\`
- macOS: `~/Library/Application Support/42-pacman/`
