import Cell



class Maze(object):
    def __init__(self, nx, ny, ix=0, iy=0):
        """Initialize the maze grid.
        The maze consists of nx x ny cells and will be constructed starting
        at the cell indexed at (ix, iy).

        """

        self.nx, self.ny = nx, ny
        self.ix, self.iy = ix, iy

        file = open("PacmanMaze")
        mazeData = file.readlines()
        mazeData = [x.strip() for x in mazeData]
        print(mazeData)
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

