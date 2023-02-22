"""This module contains logic for the minefield."""
from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger()


class MineField:
    """This class contains logic for the minefield of the minesweeper game."""

    def __init__(
        self: MineField,
        x_dim: int,
        y_dim: int,
        mine_count: int,
        random_seed: int | None,
    ) -> None:
        """Initialize minefield.

        Args:
            x_dim (int): Count of horizontal dimension.
            y_dim (int): Number of vertical dimension.
            mine_count (int): Number of mines planed on the minefield.
            random_seed (int | None): For testing purposes, the random seed can be provided.
        """
        # Store parameters:
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.mine_count = mine_count

        # If random seed provided we store it:
        self.random_seed = random_seed if random_seed else None

        # Generate matrix:
        self.reset_matrix()

    def reset_matrix(self: MineField) -> None:
        """Reset minefield based on the initial values."""
        # If provided we initialise seed:
        if self.random_seed is not None:
            np.random.seed(self.random_seed)

        # Generating mine positions and coordinates:
        mine_positions = np.sort(
            np.random.randint(0, self.x_dim * self.y_dim, size=self.mine_count)
        )
        self.mine_coordinates = np.array(
            [(int(x / self.x_dim), x % self.x_dim) for x in mine_positions]
        ).tolist()
        logger.debug(self.mine_coordinates)

        # Generate matrix with Nan-s:
        self.matrix = np.full([self.y_dim, self.x_dim], np.nan)

        # Initialize clicked fields:
        self.clicked: list[tuple] = []

    def set_cell_value(self: MineField, click: tuple, value: int) -> None:
        """Set value of the matrix for a given position.

        Args:
            click (tuple): x,y coordinate of the click
            value (int): a value to be set
        """
        self.matrix.itemset(click, value)

    def get_mine_count(self: MineField, neighbour_indices: np.ndarray) -> int:
        """Get number of mines in a provided list of position.

        Args:
            neighbour_indices (np.ndarray): list of x,y position to be checked.

        Returns:
            int: The number of mines
        """
        mines_in_neighbours = 0
        for neighbour in neighbour_indices.tolist():
            if neighbour in self.mine_coordinates:
                mines_in_neighbours += 1
        return mines_in_neighbours

    def get_matrix(self: MineField) -> np.ndarray:
        """Return the minefield as a numpy matrix.

        Returns:
            np.ndarray: unexplored fields are np.nan values.
        """
        return self.matrix

    def get_all_neighbours(self: MineField, click: tuple) -> np.ndarray:
        """For a x,y position get indices for all neighbouring cells.

        Args:
            click (tuple): x,y coordinates of a click.

        Returns:
            np.array: a list of x,y coordinatess
        """
        (x_max, y_max) = self.matrix.shape

        neighbours: list = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                # Let's skip the original coordinate:
                if j == 0 and i == 0:
                    continue

                # Calculating new coordinates:
                new_x = click[0] + i
                new_y = click[1] + j

                # Don't bother with negative coordaintes:
                if new_x < 0 or new_y < 0:
                    continue

                # Don't bother with coordaintes extending beyond the limits:
                if new_x >= x_max or new_y >= y_max:
                    continue

                neighbours.append([new_x, new_y])

        return np.array(neighbours)

    def plot_matrix_ascii(self: MineField) -> None:
        """Print out the matrix in ASCII."""
        plot = ""
        for row in self.matrix:
            for item in row:
                if item == 9 or np.isnan(item):
                    plot += "X "
                else:
                    plot += f"{int(item)} "
            plot += "\n"

        print(plot)

    def click_on(self: MineField, click: tuple) -> int:
        """Calculate effect of a click on the minefield.

        Different events might triggered:
        - If clicked on a mine, return 1
        - If field already clicked, return 2
        - If clicked on none-mine, return 0
        - If all fields are cleared, return -1

        If clicked on a zero field, recursively clicking on the neighbouring cells.

        Args:
            click (tuple): x,y coordinates of a click

        Returns:
            int: number indicating the effect of the click.
        """
        logger.debug(f"clicking on: {click}")

        # Test if we have already clicked:
        if click in self.clicked:
            logging.info(f"The field: {click} is already clicked on.")
            return 2

        # Are we clicking on a mine:
        if list(click) in self.mine_coordinates:
            print("Game over. You clicked on a mine! :(")
            return 1

        # Adding click to list:
        self.clicked.append(click)

        # 1. Get all neighbours:
        neighbours = self.get_all_neighbours(click)

        # 1. Get number of mines around the cliced cell:
        mine_count = self.get_mine_count(neighbours)

        # 2. Update value of the matrix at index:
        self.set_cell_value(click, mine_count)

        # 3. Recursion: if the value is zero, click on all the neighbours:
        if mine_count == 0:
            for neighbour in neighbours:
                if tuple(neighbour) not in self.clicked:
                    self.click_on(tuple(neighbour))

        # 4. Testing if the number of unclicked fields is the same as the number of mines:
        if len(self.mine_coordinates) == (self.x_dim * self.y_dim) - len(self.clicked):
            print("Game over. You won! :)")
            return -1

        # If we didn't win with the last click, we just keep going:
        return 0
