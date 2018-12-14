import Ghost

class RedGhost(Ghost.Ghost):

    def get_chase_target_square(self):
        enemy_x = self.pacman.get_x()
        enemy_y = self.pacman.get_y()
        self.target_square = enemy_x, enemy_y
        return (enemy_x, enemy_y)

    def set_scatter_square(self):
        self.scatter_square = (19, 0)