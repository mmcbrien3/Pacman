import Ghost

class PinkGhost(Ghost.Ghost):


    def get_chase_target_square(self):
        enemy_x = self.pacman.get_x()
        enemy_y = self.pacman.get_y()
        enemy_dir = self.pacman.direction
        
        target_x = enemy_x
        target_y = enemy_y
        if enemy_dir == "N":
            target_y -= 2
        elif enemy_dir == "S":
            target_y += 2
        elif enemy_dir == "E":
            target_x += 2
        elif enemy_dir == "W":
            target_x += 2

        self.target_square = (target_x, target_y)
        return self.target_square

    def try_to_activate(self, pellets_collected):
        self.active = True
        return True

    def set_scatter_square(self):
        self.scatter_square = (0, 0)