# Deployment checklist

The repository produces a self-contained package. The upload to itch.io
is a manual team step because it requires the team account.

## 1. Build locally

```sh
make install
make package
```

This runs PyInstaller with `42-pacman.spec`, then copies `config.json`
and `README.md` into `dist/`.

Expected local artifacts on Linux:

```text
dist/
├── 42-pacman
├── config.json
└── README.md
```

On macOS the application is `dist/42-pacman.app` and the same two
documents are copied next to it. On Windows the executable is
`dist/42-pacman.exe`.

## 2. Smoke test the package

Linux:

```sh
cd dist
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy timeout 5 ./42-pacman
echo $?
```

A timeout exit code of `124` is success. Any other non-zero code is a
failure. On a desktop session, run `./42-pacman` normally and play for
one minute.

Check that:

- the main menu opens;
- `INSTRUCTIONS` opens;
- a game starts with the bundled or adjacent `config.json`;
- a highscore is saved in the platform user-data directory;
- the process exits cleanly when the window is closed.

## 3. Collect the CI artifacts

The workflow at `.github/workflows/build.yml` builds:

| Runner | Artifact |
| --- | --- |
| Ubuntu 22.04 | `42-pacman-linux` |
| Windows latest | `42-pacman-windows` |
| macOS latest | `42-pacman-macos` |

Download each artifact from the Actions run. The macOS artifact is a
DMG. The Linux artifact is a single executable. The Windows artifact is
a single `.exe`.

## 4. Prepare the upload folders

Keep each platform in its own folder so the itch.io channels stay clean:

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

On Linux, restore the executable bit if the archive extractor dropped
it:

```sh
chmod +x release/linux/42-pacman
```

On macOS, zip the `.app` bundle if the channel expects a zip:

```sh
cd release/macos
zip -r 42-pacman-macos.zip 42-pacman.app config.json README.md
```

## 5. Upload with butler

Install butler from https://itch.io/docs/butler/ and authenticate once:

```sh
butler login
```

Push each channel. Replace `<account>/<project>` with the itch.io
project path:

```sh
butler push release/linux   <account>/<project>:linux   --userversion 1.0.0
butler push release/windows <account>/<project>:windows --userversion 1.0.0
butler push release/macos   <account>/<project>:macos   --userversion 1.0.0
```

If the macOS channel expects a zip, push the zip instead:

```sh
butler push release/macos/42-pacman-macos.zip <account>/<project>:macos --userversion 1.0.0
```

## 6. Configure the page

- Set the project visibility to draft, restricted or unlisted.
- Add a short description that says the package is an educational
  42 project.
- List the controls: arrow keys or WASD, P or Escape to pause, cheat
  keys `1` to `5`.
- Explain that a `config.json` can be placed next to the executable to
  override the defaults.
- Add the repository link and the student names tlogtenb and asylla.
- Mark the build as free.

## 7. Verify the uploaded build

1. Open the page in a private browser window.
2. Download the Linux, Windows and macOS builds.
3. Run each build and play for one minute.
4. Confirm the configuration next to the executable is read.
5. Confirm a highscore survives a restart.
6. Confirm the in-game Instructions screen is reachable from the menu.
7. Confirm the download page shows the correct version.

## 8. Final repository updates

After the upload:

- add the public itch.io URL to the project page and to the release
  notes;
- optionally add it to `README.md` under a `Public build` line;
- commit the documentation update.

## Rollback

If an uploaded channel is broken:

```sh
butler status <account>/<project>:<channel>
butler undo   <account>/<project>:<channel>
```

Then fix the build, bump the version and push again.

## Security and privacy

- Do not commit the itch.io API key or butler credentials.
- The database stores only the player name and score on the local
  machine.
- The game makes no network requests.
- The packaged build contains no analytics.

## Current status

The package recipe, the CI matrix and the local smoke test are complete.
The upload itself is pending because it requires the team's itch.io
account. The public URL is added after the upload.
