# Project management

We kept project management lightweight: a shared task list, short
check-ins when one of us started a new feature, and the git history as
the main record. This folder collects the notes we kept and the
retrospective evidence.

## Start here

- `team_organization.md`: who did what and how we split the work.
- `timeline.md`: the actual phases and dates, including the slip in the
  ghost phase.
- `project_analysis.md`: why the code is structured the way it is.
- `risk_analysis.md`: what could have gone wrong and what we did about
  it.
- `progress_tracking.md`: what was finished at each stage and what is
  left.
- `acceptance_test_plan.md`: how we tested the game, including the bug
  log.
- `blockers.md`: the problems that actually slowed us down.
- `deployment.md`: how the package is built and uploaded.

## One-minute tour

We started with the project skeleton and the configuration loader, then
spent most of July and August on the maze, movement and sprites. The
ghost work was started in August but only fully connected to the game in
October, which is the biggest slip in the project. The screens, cheats,
timer and victory flow came together in late October and early November.
The final pass was about fixing the config `level` bug, adding the
missing instructions screen, writing tests and cleaning up packaging.

If you only read two files, read `timeline.md` and
`team_organization.md`. They explain when the work happened and who did
which part.
