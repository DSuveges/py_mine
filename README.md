# py_mine

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/DSuveges/py_mine/master.svg)](https://results.pre-commit.ci/latest/github/DSuveges/py_mine/master)
[![status: experimental](https://github.com/GIScience/badges/raw/master/status/experimental.svg)](https://github.com/GIScience/badges#experimental)

A simple pygame implementation of minesweeper.

## Current state

- Minefield logic implemented.
- Custom dimensions of the minefield + custom number of mines.
- Logic on handling clicks on mine/numbered and zero field
- Flagging implemented.
- Pygame integration is lagging behind. So far only the empty field is plotted.

## Other features

- Logging enabled.
- Matrix can be plotted as ASCII characters:

```text
                1 1
      1 1 1   1 2 ⚑
      1 ⚑ 1   1 ⚑ X
1 1 1 1 X 1   1 2 X
X X X X X 1     1 ⚑
X X X X ⚑ 1     1 1
X X X X 2 1
X X X ⚑ 1
X 1 1 1 1
⚑ 1           1 1 1
1 2 1 1     1 2 ⚑ X
  1 ⚑ 1     1 ⚑ X X
  1 1 1     1 2 X X
              1 X X
```

- The object can return the numpy version of the minefield that is used for plotting by pygame.

## TODOS

- Implement pygame graphics around the logic.
- Prototype solver.
- These two stages are not dependent on each other. However I'm considering starting with the graphics to be nicer.
