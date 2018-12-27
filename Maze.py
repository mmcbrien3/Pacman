import Cell
import pygame

blockNSE = pygame.image.load("Images/BlockNSE.bmp")
blockNSW = pygame.image.load("Images/BlockNSW.bmp")
blockNEW = pygame.image.load("Images/BlockNEW.bmp")
blockSEW = pygame.image.load("Images/BlockSEW.bmp")
blockSE = pygame.image.load("Images/BlockSE.bmp")
blockSW = pygame.image.load("Images/BlockSW.bmp")
blockNS = pygame.image.load("Images/BlockNS.bmp")
blockNW = pygame.image.load("Images/BlockNW.bmp")
blockNE = pygame.image.load("Images/BlockNE.bmp")
blockEW = pygame.image.load("Images/BlockEW.bmp")
blockN = pygame.image.load("Images/BlockN.bmp")
blockS = pygame.image.load("Images/BlockS.bmp")
blockE = pygame.image.load("Images/BlockE.bmp")
blockW = pygame.image.load("Images/BlockW.bmp")
emptyBlock = pygame.image.load("Images/EmptyBlock.bmp")

class Maze(object):
    def __init__(self, nx, ny, ix=0, iy=0):
        """Initialize the maze grid.
        The maze consists of nx x ny cells and will be constructed starting
        at the cell indexed at (ix, iy).

        """

        self.no_pellet_positions = ((8, 6), (10, 6),

                       (6, 7), (7, 7), (8, 7), (9, 7),
                       (10, 7), (11, 7), (12, 7),

                       (6, 8), (9, 8), (12, 8),

                       (6, 10), (12, 10),

                       (6, 11), (7, 11), (8, 11), (9, 11),
                       (10, 11), (11, 11), (12,11),

                       (6, 12), (12, 12),

                       (0, 9), (1, 9), (2, 9), (3, 9),
                       (5, 9), (6, 9), (8, 9), (9, 9),
                       (10, 9), (12, 9), (13, 9), (15, 9),
                       (16, 9), (17, 9), (18, 9))

        self.no_turn_positions = {(8, 7): "N", (10, 7): "N", (8, 15): "N", (10, 15): "N"}

        self.nx, self.ny = nx, ny
        self.ix, self.iy = ix, iy

        file = open("PacmanMaze")
        mazeData = file.readlines()
        mazeData = [x.strip() for x in mazeData]
        x = 0
        y = 0
        for datum in mazeData:
            if x == 0 and y == 0:
                self.maze_map = [[Cell.Cell(x, y, list(datum))]]
            elif x == 0:
                self.maze_map.append([Cell.Cell(x, y, datum)])
            else:
                self.maze_map[y].append(Cell.Cell(x, y, list(datum)))
            x += 1
            if x >= self.nx:
                x = 0
                y += 1

        self.calculate_block_images()

    def calculate_block_images(self):
        self.block_images = []
        for cell in self.list_cells():
            blockImage = None
            screen_x = cell.get_x() * 32
            screen_y = cell.get_y() * 32
            walls = self.get_cells_walls(cell)
            walls.sort()
            if len(walls) == 0 or len(walls) == 4:
                blockImage = emptyBlock
            elif walls == ["E", "W"]:
                blockImage = blockEW
            elif walls == ["N", "S"]:
                blockImage = blockNS
            elif walls == ["E", "N"]:
                blockImage = blockNE
            elif walls == ["E", "N", "W"]:
                blockImage = blockNEW
            elif walls == ["E", "N", "S"]:
                blockImage = blockNSE
            elif walls == ["N", "S", "W"]:
                blockImage = blockNSW
            elif walls == ["N", "W"]:
                blockImage = blockNW
            elif walls == ["E", "S"]:
                blockImage = blockSE
            elif walls == ["E", "S", "W"]:
                blockImage = blockSEW
            elif walls == ["S", "W"]:
                blockImage = blockSW
            elif walls == ["S"]:
                blockImage = blockS
            elif walls == ["W"]:
                blockImage = blockW
            elif walls == ["N"]:
                blockImage = blockN
            elif walls == ["E"]:
                blockImage = blockE
            self.block_images.append((blockImage, (screen_x, screen_y)))

    def get_block_images(self):
        return self.block_images

    def get_legal_directions(self, x, y):
        directions = ["N", "S", "E", "W"]
        legal = []
        for dir in directions:
            if self.is_path_legal(x, y, dir):
                legal.append(dir)
        return legal

    def get_legal_neighbors(self, x, y):
        dirs = self.get_legal_directions(x, y)
        legal = []
        for d in dirs:
            if d == "N":
                legal.append((x, y - 1))
            elif d == "S":
                legal.append((x, y + 1))
            elif d == "E":
                legal.append((x + 1, y))
            elif d == "W":
                legal.append((x - 1, y))
        return legal

    def is_path_legal(self, x, y, dir):
        if dir == "":
            return True
        cur_cell = self.cell_at(x, y)
        if cur_cell.walls[dir]:
            return False
        return True

    def is_cell_critical(self, x, y):
        dirs = self.get_legal_directions(x, y)
        if len(dirs) <= 2:
            return False
        return True
    
    def get_neighbors(self, x, y):
        neighbors = {}
        if x == 0:
            neighbors["W"] = Cell.Cell(0, 0, ["N", "S", "E", "W"])
            neighbors["E"] = self.cell_at(x + 1, y)
        elif x == self.nx - 1:
            neighbors["E"] = Cell.Cell(0, 0, ["N", "S", "E", "W"])
            neighbors["W"] = self.cell_at(x - 1, y)
        else:
            neighbors["W"] = self.cell_at(x - 1, y)
            neighbors["E"] = self.cell_at(x + 1, y)
        if y == 0:
            neighbors["N"] = Cell.Cell(0, 0, ["N", "S", "E", "W"])
            neighbors["S"] = self.cell_at(x, y + 1)
        elif y == self.ny - 1:
            neighbors["S"] = Cell.Cell(0, 0, ["N", "S", "E", "W"])
            neighbors["N"] = self.cell_at(x, y - 1)
        else:
            neighbors["N"] = self.cell_at(x, y - 1)
            neighbors["S"] = self.cell_at(x, y + 1)
        return neighbors


    def get_position_in_direction(self, x, y, d):
        x_ret = x
        y_ret = y
        if d == "N":
            y_ret -= 1
        elif d == "S":
            y_ret += 1
        elif d == "E":
            x_ret += 1
        elif d == "W":
            x_ret -= 1

        return (x_ret, y_ret)
    
    def get_cells_walls(self, cell):
        walls = []
        if not cell.is_block():
            return walls
        else:
            ns = self.get_neighbors(cell.get_x(), cell.get_y())
            for d, n in ns.items():
                if not n.is_block():
                    walls.append(d)
            return walls
            

    def cell_at(self, x, y):
        """Return the Cell object at (x,y)."""

        return self.maze_map[y][x]

    def list_cells(self):
        cells = []
        for x in range(self.nx):
            for y in range(self.ny):
                cells.append(self.maze_map[y][x])
        return cells


    def write_svg(self, filename):
        """Write an SVG image of the maze to filename."""

        aspect_ratio = self.nx / self.ny
        # Pad the maze all around by this amount.
        padding = 10
        # Height and width of the maze image (excluding padding), in pixels
        height = 500
        width = int(height * aspect_ratio)
        # Scaling factors mapping maze coordinates to image coordinates
        scy, scx = height / self.ny, width / self.nx

        def write_wall(f, x1, y1, x2, y2):
            """Write a single wall to the SVG image file handle f."""

            print('<line x1="{}" y1="{}" x2="{}" y2="{}"/>'
                  .format(x1, y1, x2, y2), file=f)

        # Write the SVG image file for maze
        with open(filename, 'w') as f:
            # SVG preamble and styles.
            print('<?xml version="1.0" encoding="utf-8"?>', file=f)
            print('<svg xmlns="http://www.w3.org/2000/svg"', file=f)
            print('    xmlns:xlink="http://www.w3.org/1999/xlink"', file=f)
            print('    width="{:d}" height="{:d}" viewBox="{} {} {} {}">'
                  .format(width + 2 * padding, height + 2 * padding,
                          -padding, -padding, width + 2 * padding, height + 2 * padding),
                  file=f)
            print('<defs>\n<style type="text/css"><![CDATA[', file=f)
            print('line {', file=f)
            print('    stroke: #000000;\n    stroke-linecap: square;', file=f)
            print('    stroke-width: 5;\n}', file=f)
            print(']]></style>\n</defs>', file=f)
            # Draw the "South" and "East" walls of each cell, if present (these
            # are the "North" and "West" walls of a neighbouring cell in
            # general, of course).
            for x in range(self.nx):
                for y in range(self.ny):
                    if self.cell_at(x, y).walls['S']:
                        x1, y1, x2, y2 = x * scx, (y + 1) * scy, (x + 1) * scx, (y + 1) * scy
                        write_wall(f, x1, y1, x2, y2)
                    if self.cell_at(x, y).walls['E']:
                        x1, y1, x2, y2 = (x + 1) * scx, y * scy, (x + 1) * scx, (y + 1) * scy
                        write_wall(f, x1, y1, x2, y2)
            # Draw the North and West maze border, which won't have been drawn
            # by the procedure above.
            print('<line x1="0" y1="0" x2="{}" y2="0"/>'.format(width), file=f)
            print('<line x1="0" y1="0" x2="0" y2="{}"/>'.format(height), file=f)
            print('</svg>', file=f)

