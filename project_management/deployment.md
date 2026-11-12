# Deployment

The game is packaged with PyInstaller and published on itch.io at
https://shadowthijs.itch.io/42-pacman. The upload is done by hand with
butler.

## Build the package

```sh
make install
make package
```

`make package` runs `42-pacman.spec` and then copies `config.json` and
`README.md` next to the build. On Linux the output is:

```text
dist/
├── 42-pacman
├── config.json
└── README.md
```

On Windows the executable is `dist/42-pacman.exe`. On macOS the app is
`dist/42-pacman.app`.

## Check the build

Run the Linux smoke test:

```sh
cd dist
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy timeout 5 ./42-pacman
echo $?
```

`124` means the game was still running when the timeout fired, which is
what we want. Any other non-zero code is a problem. On a desktop, just
run `./42-pacman` and play for a minute.

Check that the menu opens, the instructions screen works, a game starts
with the config next to the executable, a score is saved, and the
window closes cleanly.

## Gather the CI artifacts

The workflow in `.github/workflows/build.yml` builds three artifacts:

| Runner | Artifact |
| --- | --- |
| Ubuntu 22.04 | `42-pacman-linux` |
| Windows latest | `42-pacman-windows` |
| macOS latest | `42-pacman-macos` |

Download them from the Actions run. The Linux and Windows artifacts
contain the executable, `config.json` and `README.md`. The macOS
artifact is a DMG with the app and both documents inside.

## Put each platform in its own folder

```text
release/
├── linux/
│   ├── 42-pacman
│   ├── config.json
│   └── README.md
├── windows/
│   ├── 42-pacman.exe
│   ├── config.json
│   └── README.md
└── macos/
    ├── 42-pacman.app
    ├── config.json
    └── README.md
```

On Linux, restore the executable bit if the extractor dropped it:

```sh
chmod +x release/linux/42-pacman
```

If the macOS channel wants a zip, make one:

```sh
cd release/macos
zip -r 42-pacman-macos.zip 42-pacman.app config.json README.md
```

## Upload with butler

Install butler from https://itch.io/docs/butler/ and log in once:

```sh
butler login
```

Push each channel to the published project:

```sh
butler push release/linux   shadowthijs/42-pacman:linux   --userversion 1.0.0
butler push release/windows shadowthijs/42-pacman:windows --userversion 1.0.0
butler push release/macos/42-pacman-macos.zip shadowthijs/42-pacman:macos --userversion 1.0.0
```

## Page settings

- Set the project to draft, restricted or unlisted.
- Mark it as a free educational project from 42.
- List the controls: arrow keys or WASD, P or Escape to pause, keys `1`
  to `5` for cheats.
- Mention that a `config.json` next to the executable overrides the
  defaults.
- Add the repository link and the names tlogtenb and asylla.

## After upload

1. Open the page in a private window.
2. Download each platform build.
3. Run it and play for a minute.
4. Confirm the config next to the executable is read.
5. Confirm a highscore survives a restart.
6. Confirm the instructions screen is reachable.
7. Confirm the public URL is listed in the README and project page:
   https://shadowthijs.itch.io/42-pacman

If a channel is broken, `butler status` and `butler undo` can roll it
back before you push a fixed build.

## Notes

- Do not commit the itch.io API key or butler credentials.
- The game makes no network requests.
- The database stores only the player name and score on the local
  machine.
- The package builds and smoke tests pass.
- The published build is available at
  https://shadowthijs.itch.io/42-pacman.
