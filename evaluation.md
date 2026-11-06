# Pac-Man evaluation

## Introduction
- Remain polite, courteous, respectful and constructive throughout the evaluation process. The well-being of the community depends on it.
- Identify with the person (or the group) evaluated the eventual dysfunctions of the work. Take the time to discuss and debate the problems you have identified.
- YOu must consider that there might be some difference in how your peers might have understood the projects's instructions and the scope of its functionalities. Always keep an open mind and grade him/her as honestly as possible. The pedagogy is valid only and only if peer-evaluation is conducted seriously.

## Guidelines
- Only grtade the work that is in the student or group's git repository.
- Double-check that the git repository belong to the student or the group. Ensure that the work is for the relevant project and also check that git clone is used in an empty folder.
- To avoid any surprises, carefully check that both the evluating and the evluated students have reviewd the possible scripts used to facilitate the grading.
- If the evluating student has not completed that particular project yet, it is madatory for this student to read the entire subject prior to starting the defence.
- Use the flags available on this scale to signal an empty repository, non-functioning program, a norm error, cheating etc. In these cases, the grading is over and the final grade is 0 (or -42 in case of cheating). However, with the exception of cheating, you are encouraged to continue to discuss your work (even if you have not finished it) in order to identify any issues that may have caused this failure and avoid repeating the same mistake in the future.
- Remember that for the duration of the defence, no segfault, no other unexpected, premature, uncontrolled or unexpected termination of the program, else the final grade is 0. Use the appropriate flag. You should never have to edit any file except the configuration file if it exists. If you want to edit a file, take the time to explicit the reasons with the evaluated student and make sure both of you are okay with this.
- You must also verify the absence of memory leaks. Any memory allocated on the heap must be properly freed before the end of execution. You are allowed to use any of the different tools available on the computer, such as leaks, valgrind, or e_fence. In case of memory leaks, tick the appropriate flag.

## Attachments

[subject.pdf](https://cdn.intra.42.fr/pdf/pdf/220990/en.subject.pdf)
[mazegenerator-00001.zip](https://cdn.intra.42.fr/document/document/54929/mazegenerator-00001.zip)

## Preliminaries

### Basics
- Only grade the work that is in the student's or group's git repository.
- All the files requested in the subject must be present in the repository.

[ Yes ] [ No ]

## Mandatory Part

### Project Management

Check the dedicated subdirectory for the project management

- It must include relevant elements, like the examples provided in the subject.
- Ask the team to pitch a one-minute tour of the documents.

You should have a clear view of how the project was managed and organized.
If it is not the case, the evaluation stops here.

[ Yes ] [ No ]

### README.md File

Check if the README.md file is present at the root of the project and includes all the required sections as described in the subject.

Along with the usual 4 required elements, Pac-Man asks for 6 extra sections. Other relevant sections / elements are allowed in this file.

[ Yes ] [ No ]

### Makefile

Check if the Makefile is present at the root of the project and includes the rules required in the subject.

If any of the required rules is missing, the grade is 0.

[ Yes ] [ No ]

### Code Quality

Quality checks pass on the Python sources:
run `make lint`
- `flake8`: No errors or warnings
- `mypy`: No errors, no warnings

[ Yes ] [ No ]

### Usage (CLI)

Run `make install` to create the appropriate runtime environment.
If needed, enter into a virtualenv.

- Check that the program usage matches the subject exactly one argument (a JSON config file).
- Wrong/missing arguments must be handled with clear messages (no Python traceback).
- Also check in the Makefile that the `run` rule follows the expected usage.

[ Yes ] [ No ]

### Configuration File

Check the the configuration is present and follows the requirements described in the subject:

- format, comments handling, defaults/clamping, unknown keys, etc.

[ Yes ] [ No ]

### Error Handling

For the upcoming questions, every time the program is running:

- Check that errors are handled cleanly with clear messages.
- Check that no Python traceback is ever displayed to the user.

If not, hit the 'Crash' flag.

[ Yes ] [ No ]

### Build and Run

Follow the instructions provided in the README.md file.

- Check that running `make run` is also a valid way to launch the program.

[ Yes ] [ No ]

### Main Menu

The application starts at the main menu and displays the elements required in the subject.

- A way to start a new game
- A Highscore view
- Instructions with the game rules and controls
- A way to quit the game

[ Yes ] [ No ]

### Level Structure

Time to start the game!

- Ensure that the first level is always the same (fixed seed).
- Check that the level structure is correctly implemented and follows the requirements in the subject:
  - corridors, pacgums, super pacgums, walls, player and ghosts.

[ Yes ] [ No ]

### Player Mechanics

Check that the player mechanics are correctly implements and follow the requirements in the subject.

- You can move in the maze
- You can't cross walls
- You can eat pacgums and super pacgums
- YOu can die and re-spawn

[ Yes ] [ No ]

### Ghost Mechanics

Check that the ghosts mechanics are correctly implemented and follow the requirements in the subject.

- They can autonomously chase you or filee you according to the situation
- They can be eatenb and they re-spawn after a while

[ Yes ] [ No ]

### Pacgum and Super-Pacgum

Check that the pacgum and super-pacgum mechanics are correctly implemented and follow the requirements in the subject.

- Pacgums are present in the maze and can be eaten
- Super-pacgums are present in the maze and can be eaten
- Eating a pacgum increases the score appropriately
- Eating a super-pacgum makes the ghosts flee for a limited time

[ Yes ] [ No ]

### Scoring system

The score shouldbe displayed during the game, and increase based on the different actions (eating a pacgum, a super-pacgum, a ghost).

[ Yes ] [ No ]

### Cheat Mode

The cheat mode is provided to facilitate testing and debugging.

- Ask the team to present the available cheat modes in the program and test them.

[ Yes ] [ No ]

### Game Progression

Check that the game progression is correctly implemented and follows the requirements in the subject.

- Complete a full cycle:
  - starting a brand new game
  - Try to lose your lives, eating pacgums and super-pacgums
  - Win or lose the level
  - Add your name to the higschore board

[ Yes ] [ No ]

### Highscore Persistence

Check that the highscore system is correctly implemented and persistent.

- It must follow the requirements in the subject.
- Ask the team their choices regarding persistent storage.
- Control the full process:
- Control the full process:
  - Start with an empty highscore board
  - Then, win or lose a level
  - Then, enter your name for the highscore board
  - Then, quit the game
  - Finally, Start again to see your previous score.

[ Yes ] [ No ]

### User Interface

Check user interface elements not controlled yet:
In the subject check the User Interface chapter to see what is required.

- The Main menu displays all the required elements?
- The In-Game HUD displays all the required elements?
- The pause menu displays all the required elements?
- The game over screen displays all the required elements?
- The victory screen displays all the required elements?

[ Yes ] [ No ]

### Maze Generator Integration

Check that the assigned maze generator package is indeed used, and not altered.

- Download again the package and re-install it.
- The pac-man program should work as previously.
- Control in the code that the package is actually used and not just discarded.

[ Yes ] [ No ]

### Object Oriented Programming

Check that the code is organized in an object-oriented structure.

- You should see classes for each different logic elements, and the code should benefit from the classic OOP approach. Example: the same "do not cross walls" rule should be inherited by pac-man and ghosts.
- Do not hesitate to ask the team to explain their choices and structure. Keep in mind that there is not a unique approach.

[ Yes ] [ No ]

### Project packagin and Deployment on Gaming Playform

The project is packaged for publication as described in the subject.

- You should be able to re-generate the package live during this evaluation.
- Check that the package is available for download on a gaming platform.
- It is not mandatory to upload the re-generated package online during the evaluation as it may require some validation from the gaming platform.

[ Yes ] [ No ]

## Ratings

[ Ok ] [ Outstanding project ]
[ Empty work ] [ Incomplete work ] [ Invalid compilation ] [ Norme ] [ Cheat ] [ Crash ]
[ Incomplete group ] [ Concerning situation ] [ Leaks ] [ Forbidden function ]
[ Can't support / explain code ]
