"""This is the main script to run minesweeper."""

from __future__ import annotations

import logging
import sys
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

        # Initialize text on matrix:
        self.font = pygame.font.SysFont(
            "novamono", int(self.unit_length * 1), bold=True
        )

        # Filling with background color:
        self.display.fill(cfg.plot_parameters.clicked.base_color)

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

    def plot(
        self: MineFieldPlot, minefield_matrix: ndarray, flags: list[tuple]
    ) -> None:
        """Main loop for plotting values in the matrix.

        Args:
            minefield_matrix (ndarray): Minefield matrix
            flags (list): List of flag coordinates:
        """
        # Filling with background color:
        self.display.fill(self.cfg.plot_parameters.clicked.base_color)

        # Looping through the matrix both dimensions:
        for x in range(self.cfg.matrix_parameters.x_dim):
            for y in range(self.cfg.matrix_parameters.y_dim):
                matrix_value = minefield_matrix[x, y]
                scaled_coordinates = self.scale_coordinate((x, y))

                # Drawing unclicked:
                if np.isnan(matrix_value):
                    self.plot_nan(scaled_coordinates)
                # Drawing cliced:
                else:
                    self.plot_number(scaled_coordinates, matrix_value)

        # Adding flags:
        for flag in flags:
            scaled_coordinates = self.scale_coordinate(flag)
            self.plot_flag(scaled_coordinates)

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
        """_summary_Plotting clicked fields with numbers.

        Args:
            coordinates (tuple): Scaled coordinales for the clicked field
            number (int): Number in the clicked field
        """
        border_color = self.cfg.plot_parameters.clicked.border_color
        rect_dim = [
            coordinates[0],  # x coordinate shifted to the right by the offset
            coordinates[1],  # y coordinate shifted to the bottom by the offset
            self.unit_length,  #
            self.unit_length,
        ]
        pygame.draw.rect(self.display, border_color, rect_dim, 1)

        # return if the number is zero:
        if number == 0:
            return

        # Plot number:
        number_color = self.cfg.plot_parameters.clicked.number_colors[int(number - 1)]

        label = self.font.render(str(int(number)), True, number_color)
        x_center_offset = self.unit_length / 3

        self.display.blit(label, (coordinates[0] + x_center_offset, coordinates[1]))

    def plot_flag(self: MineFieldPlot, coordinates: tuple) -> None:
        """Draw flags on the minefield.

        Args:
            coordinates (tuple): x,y coordinates of the flag.
        """
        base_color = self.cfg.plot_parameters.flag.base_color
        flag_color = self.cfg.plot_parameters.flag.flag_color

        # Scaled coordinates for base:
        (x, y) = coordinates

        # Drawing the flag:
        flag_coordinates = [(0.5, 0.2), (0.6, 0.2), (0.6, 0.5), (0.5, 0.5), (0.2, 0.35)]
        pygame.draw.polygon(
            self.display,
            flag_color,
            [
                (x + self.unit_length * f[0], y + self.unit_length * f[1])
                for f in flag_coordinates
            ],
        )

        # Drawing the flag base:
        flag_base_coordinates = [
            (0.5, 0.5),
            (0.6, 0.5),
            (0.6, 0.7),
            (0.8, 0.75),
            (0.8, 0.8),
            (0.2, 0.8),
            (0.2, 0.75),
            (0.5, 0.7),
        ]
        pygame.draw.polygon(
            self.display,
            base_color,
            [
                (x + self.unit_length * f[0], y + self.unit_length * f[1])
                for f in flag_base_coordinates
            ],
        )

    def plot_mine(self: MineFieldPlot, coordinates: tuple) -> None:
        """Not implemented.

        Args:
            coordinates (tuple): _description_

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    def screen_to_matrix_position_convert(self: MineFieldPlot, pos: tuple) -> tuple:
        """Convert screen coordinates to matrix coordinates.

        Args:
            pos (tuple): Screen coordinates captured by pygame.

        Returns:
            tuple: Converted coordinates with a tuple.
        """
        return (int(pos[0] / self.unit_length), int(pos[1] / self.unit_length))


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
        self.plotter.plot(self.mine_field.get_matrix(), self.mine_field.flagged)
        pygame.display.flip()

    def play(self: MineSweeper) -> None:
        """Main loop that handles gameplay."""
        while True:
            events = pygame.event.get()

            for event in events:
                if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_x):
                    print("Escape!!")
                    pygame.quit()
                    break

                # handle MOUSEBUTTONUP
                elif event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    # Click on field:
                    if event.button == 1:
                        self.mine_field.click_on(
                            self.plotter.screen_to_matrix_position_convert(pos)
                        )
                    # Flagging:
                    elif event.button == 3:
                        self.mine_field.flag_field(
                            self.plotter.screen_to_matrix_position_convert(pos)
                        )

                    # After any event, we re-plot the field:
                    self.plotter.plot(
                        self.mine_field.get_matrix(), self.mine_field.flagged
                    )
                    pygame.display.flip()


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
