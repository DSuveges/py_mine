"""This is the main script to run minesweeper."""
from __future__ import annotations

import logging
import sys
import time
from typing import TYPE_CHECKING

import hydra
import numpy as np
import pygame

from modules.mine_field import MineField

if TYPE_CHECKING:
    from numpy import ndarray
    from omegaconf import DictConfig
    from pygame import Surface


class MineFieldPlot:
    """Plotting infrastucture for MineSweeper."""

    def __init__(self: MineFieldPlot, cfg: DictConfig, display: Surface) -> None:
        """Initialize plotter object by providing configuration and the display object.

        Args:
            cfg (DictConfig): hydra configuration
            display (Surface): PyGame display object
        """
        self.cfg = cfg
        self.display = display
        self.unit_length = self.cfg.plot_parameters.unit_length
        self.unit_offset = self.unit_length / 10

    def scale_coordinate(self: MineFieldPlot, coordinates: tuple) -> tuple:
        """Scale x,y coordinates of the matrix to screen.

        Args:
            coordinates (tuple): x,y coordinates of a value in the matrix.

        Returns:
            tuple: Scaled coordinate to screen.
        """
        return (
            coordinates[0] * self.unit_length,
            coordinates[1] * self.unit_length,
        )

    def plot(self: MineFieldPlot, minefield_matrix: ndarray) -> None:
        """Main loop for plotting values in the matrix.

        Args:
            minefield_matrix (ndarray): Minefield matrix
        """
        # Looping through the matrix both directions:
        for x in range(self.cfg.matrix_parameters.x_dim):
            for y in range(self.cfg.matrix_parameters.y_dim):
                value = minefield_matrix[x, y]
                scaled_coordinates = self.scale_coordinate((x, y))

                if np.isnan(value):
                    self.plot_nan(scaled_coordinates)

    def plot_nan(self: MineFieldPlot, coordinates: tuple) -> None:
        """Plotting unexplored fields in the matrix.

        Args:
            coordinates (tuple): scaled coordinate of field.
        """
        # Get color definitions:
        rgb = self.cfg.plot_parameters.unclicked.base_color
        rgb_lighter = self.cfg.plot_parameters.unclicked.light_color
        rgb_darker = self.cfg.plot_parameters.unclicked.dark_color

        # Scaling coordinates:
        (x, y) = coordinates

        # Drawing the two triangles:
        pygame.draw.polygon(
            self.display,
            rgb_lighter,
            [(x, y), (x + self.unit_length, y), (x, y + self.unit_length)],
        )
        pygame.draw.polygon(
            self.display,
            rgb_darker,
            [
                (x + self.unit_length, y),
                (x, y + self.unit_length),
                (x + self.unit_length, y + self.unit_length),
            ],
        )

        # rectangle dimensions:
        rect_dim = [
            x + self.unit_offset,  # x coordinate shifted to the right by the offset
            y + self.unit_offset,  # y coordinate shifted to the bottom by the offset
            self.unit_length - (2 * self.unit_offset),  # Scaling down the rectangle
            self.unit_length - (2 * self.unit_offset),
        ]
        pygame.draw.rect(self.display, rgb, rect_dim)

    def plot_number(self: MineFieldPlot, coordinates: tuple, number: int) -> None:
        """Not implemented.

        Args:
            coordinates (tuple): _description_
            number (int): _description_

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    def plot_flag(self: MineFieldPlot, coordinates: tuple) -> None:
        """Not implemented.

        Args:
            coordinates (tuple): _description_

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    def plot_mine(self: MineFieldPlot, coordinates: tuple) -> None:
        """Not implemented.

        Args:
            coordinates (tuple): _description_

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError


class MineSweeper:
    """Game main logic."""

    def __init__(self: MineSweeper, cfg: DictConfig, display: Surface) -> None:
        """By providing configuration the game object is initialized."""
        # Initialize minefield with parameters:
        self.mine_field = MineField(
            x_dim=cfg.matrix_parameters.y_dim,
            y_dim=cfg.matrix_parameters.x_dim,
            mine_count=cfg.matrix_parameters.mine_count,
        )

        # Store display:
        self.display = display
        self.clock = pygame.time.Clock()

        # Initialize plotter:
        self.plotter = MineFieldPlot(cfg, display)

        # Plot minefield:
        self.plotter.plot(self.mine_field.get_matrix())

    def play(self: MineSweeper) -> None:
        """Main loop that handles gameplay."""
        while True:
            pygame.display.flip()
            time.sleep(5)


@hydra.main(version_base=None, config_path="configuration", config_name="config")
def main(cfg: DictConfig) -> None:
    """Game function.

    Args:
        cfg (DictConfig): hydra configuration with parameters.
    """
    # Get the display dimensions:
    width: int = cfg.matrix_parameters.x_dim * cfg.plot_parameters.unit_length
    height: int = cfg.matrix_parameters.y_dim * cfg.plot_parameters.unit_length

    # Genertaing the display:
    pygame.init()
    display = pygame.display.set_mode([width, height])

    # Initialize MineSweeper with parameters:
    minesweeper = MineSweeper(cfg, display)
    minesweeper.play()


if __name__ == "__main__":

    # Initialize logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    main()
