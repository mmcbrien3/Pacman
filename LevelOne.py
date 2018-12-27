import pygame
import Maze, LevelTwo

class LevelOne(object):

    def __init__(self):
        self.maze_file = "PacmanMaze"
        self.maze = Maze.Maze(19, 21, self.maze_file)
        self.pacman_speed = 4
        self.ghost_speed = 3
        self.ghost_sequences = [[20, 7]]
        self.number = 1

    def get_next_level(self):
        return LevelTwo.LevelTwo()
