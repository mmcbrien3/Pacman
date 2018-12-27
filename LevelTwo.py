import pygame
import Maze

class LevelTwo(object):

    def __init__(self):
        self.maze_file = "PacmanMaze"
        self.maze = Maze.Maze(19, 21, self.maze_file)
        self.pacman_speed = 5
        self.ghost_speed = 4
        self.ghost_sequences = [[20, 5]]
