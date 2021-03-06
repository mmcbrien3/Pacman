import math

class Ghost(object):

    def __init__(self, x, y, maze, speed, pacman, block_size):
        self.position = (x, y)
        self.direction = "E"
        self.maze = maze
        self.speed = speed
        self.pacman = pacman
        self.block_size = block_size
        self.target_square = (0, 0)
        self.last_decision_position = None
        self.screen_position = (x * block_size, y * block_size)

        self.set_scatter_square()
        self.chasing = False
        self.scattering = True
        self.active = False
        self.mode_changed = False

        self.cage_squares = ((9, 8), (8, 9), (9, 9), (10, 9))

    def set_scatter_square(self):
        pass

    def get_chase_target_square(self):
        pass

    def try_to_activate(self, pellets_collected):
        pass

    def get_scatter_target_square(self):
        self.target_square = self.scatter_square
        return self.target_square

    def get_target_square(self):
        if self.active:
            if self.position in self.cage_squares:
                self.target_square = (9, 8)
                return self.target_square
            elif self.chasing:
                return self.get_chase_target_square()
            elif self.scattering:
                return self.get_scatter_target_square()
        else:
            self.target_square = (9, 10)
            return self.target_square

    def get_cur_image(self):
        if self.image_count + 1 < len(self.images):
            self.image_count += 1
        else:
            self.image_count = 0
        return self.images[self.image_count]

    def get_inactive_target_square(self):
        self.target_square = (9, 10)
        return self.target_square

    def get_screen_x(self):
        return self.screen_position[0]

    def get_screen_y(self):
        return self.screen_position[1]

    def set_screen_position(self, x, y):
        self.screen_position = (x, y)

    def set_position(self, x, y):
        self.position = (x, y)

    def get_opposite_direction(self):
        if self.direction == "N":
            return "S"
        elif self.direction == "S":
            return "N"
        elif self.direction == "E":
            return "W"
        elif self.direction == "W":
            return "E"

    def update_mode(self):
        self.chasing = not self.chasing
        self.scattering = not self.scattering
        self.mode_changed = True

    def update_direction(self):
        if self.mode_changed:
            self.last_decision_position = self.maze.get_position_in_direction(
                self.position[0],
                self.position[1],
                self.direction)
            self.direction = self.get_opposite_direction()
            self.mode_changed = False
            return
        if not self.maze.is_cell_critical(self.position[0], self.position[1]) and self.maze.is_path_legal(self.position[0], self.position[1], self.direction)\
                or not self.is_in_center():
            return
        self.direction = self.get_movement_direction()

    def is_in_center(self):
        if self.get_screen_x() % self.block_size == 0 and self.get_screen_y() % self.block_size == 0:
            return True
        return False

    def get_movement_direction(self):
        if self.last_decision_position == self.position:
            return self.direction
        self.last_decision_position = self.position
        target = self.get_target_square()
        target_x = target[0]
        target_y = target[1]
        options = self.maze.get_legal_neighbors(self.position[0], self.position[1])
        try:
            options.remove(self.maze.get_position_in_direction(self.position[0], self.position[1], self.get_opposite_direction()))
        except:
            pass

        directions = self.maze.get_legal_directions(self.position[0], self.position[1])
        try:
            directions.remove(self.get_opposite_direction())
        except:
            pass

        if self.position in self.maze.no_turn_positions:
            try:
                options.remove(self.maze.get_position_in_direction(self.position[0], self.position[1], self.maze.no_turn_positions[self.position]))
                directions.remove(self.maze.no_turn_positions[self.position])
            except:
                pass
        if len(options) == 0:
            return self.get_opposite_direction()
        min_o = math.sqrt((options[0][0] - target_x) ** 2 + (options[0][1] - target_y) ** 2)
        ind = 0
        for i, o in enumerate(options[1:]):
            opt_x = o[0]
            opt_y = o[1]
            dist = math.sqrt((opt_x - target_x) ** 2 + (opt_y - target_y) ** 2)
            if dist < min_o:
                min_o = dist
                ind = i + 1
        selection = directions[ind]
        return selection

