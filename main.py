from random import randrange


class Maze:
    def __init__(self, tiles: list[list[int]] = None):
        self.tiles = tiles
        self.size_x = len(self.tiles[0])
        self.size_y = len(self.tiles)
        self.entrances = None
        self.solved = False
        self.path = None
        self.path_support = set()

    def __str__(self):
        def paint(tile: int) -> str:
            return ('  ', '\u2588\u2588', '//')[tile]
        return '\n'.join([''.join(tuple(map(paint, row))) for row in self.tiles])

    @classmethod
    def create_maze(cls, size_x: int, size_y: int):
        """
        :param size_x: width of the maze grid
        :param size_y: height of the maze grid
        :return: Maze instance of specified height and width, with randomly generated paths and exactly two entrances
        """
        instance = cls([[1 for _ in range(size_x)] for _ in range(size_y)])
        instance.generate()
        instance.create_entrances()
        return instance

    @classmethod
    def from_file(cls, filename: str):
        """

        :param filename: filename that refers to txt file
        :return: Maze instance reflecting contents of the file
        """
        with open(f"{filename}.txt", "r") as file:
            instance = cls([list(map(int, [a for a in line.strip()])) for line in file])
        instance.find_entrances()
        return instance

    def save_to_file(self, filename: str):
        with open(f"{filename}.txt", "w") as file:
            for line in self.tiles:
                file.write("".join(map(str, line)) + "\n")

    def create_entrances(self):
        """
        Creates exactly two entrances, in respectively first and last column, i.e. left and right side of the Maze.
        Both entrances have random position that cannot be a corner. From this position a "tunnel" is then carved until
        it encounters any tile that is not a wall.
        """
        self.entrances = ((randrange(1, self.size_y - 1, 2), 0), (randrange(1, self.size_y - 1, 2), self.size_x - 1))
        for y, x in self.entrances:
            self.tiles[y][x] = 0
            if x == 0:
                i = 1
                while x < self.size_x - 1:
                    if self.tiles[y][x + i] != 0:
                        self.tiles[y][x + i] = 0
                    else:
                        break
            elif x == self.size_x-1:
                i = 1
                while x > 0:
                    if self.tiles[y][x - i] != 0:
                        self.tiles[y][x - i] = 0
                    else:
                        break

    def find_entrances(self):
        """
        Finds entrances in a maze and stores them in variable that can be later used by solve_maze
        """
        entrances = []
        for i, row in enumerate(self.tiles):
            if row[0] == 0:
                entrances.append((i, 0))
        for i, row in enumerate(self.tiles):
            if row[self.size_x - 1] == 0:
                entrances.append((i, self.size_x - 1))
        self.entrances = entrances

    def generate(self):
        """
        Carves random paths inside the Maze grid using Prim's algorithm for Minimum Spanning Tree.
        Between any two points of the created Maze there is exactly one path.
        """
        rand_y, rand_x = (randrange(1, self.size_x - 1, 2), randrange(1, self.size_y - 1, 2))
        nodes = set()
        nodes.add((rand_y, rand_x, rand_y, rand_x))
        while nodes:
            y, x, y1, x1 = nodes.pop()
            if self.tiles[y][x] == 1:
                self.tiles[y][x] = 0
                self.tiles[y1][x1] = 0
                nodes.update(self.find_nodes((y, x)))

    def find_nodes(self, node: tuple[int, ...], solve: bool = False) -> set[tuple[int, ...]]:
        """
        Finds surrounding tiles that meet the requirements and returns them
        :param node: node of which surrounding will be examined
        :param solve: when False, functions looks for surrounding wall tiles, otherwise it looks for surrounding
        path tiles.
        """
        nodes = set()
        if solve:
            axis = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            offset = 0
        else:
            axis = [(-2, 0), (2, 0), (0, -2), (0, 2)]
            offset = 1
        for i, j in axis:
            if (0 < node[0] + i < self.size_y - 1 and
                    0 < node[1] + j < self.size_x - offset and
                    self.tiles[node[0] + i][node[1] + j] == offset):
                if solve:
                    nodes.add((node[0] + i, node[1] + j))
                else:
                    nodes.add((node[0] + i, node[1] + j, node[0] + i // 2, node[1] + j // 2))
        return nodes

    def solve_maze(self, node: tuple[int, ...] = None, path: list[tuple[int]] = None):
        """
        Solves maze by checking every possible path from the entrance until it finds another entrance.
        All concurrent function instances are stopped when entrance is found.
        :param node: node where function starts looking for possible path
        :param path: current path of function instance, it avoids searching repetitions
        :return:
        """
        self.path_support.add(node)
        if node is None:
            node = self.entrances[0]
        if path is None:
            path = []
        if self.solved:
            return
        if node == self.entrances[1]:
            self.path = path + [node]
            self.solved = True
        for new_node in self.find_nodes(node, solve=True).difference(self.path_support):
            self.solve_maze(new_node, path + [node])

    def printable_solved_maze(self):
        """
        Invokes solve_maze if Maze has not been already solved. Adds solution path to Maze grid.
        """
        if not self.solved:
            self.solve_maze()
        for y, x in self.path:
            self.tiles[y][x] = 2


class Menu:
    def __init__(self):
        self.maze = None
        self.text = {"1": "Generate a new maze.", "2": "Load a maze.", "3": "Save the maze.",
                     "4": "Display the maze.", "5": "Find the escape.", "0": "Exit."}

    def display(self):
        print("=== Menu ===")
        for key, value in self.text.items():
            if key in ["3", "4"] and self.maze is None:
                continue
            print(f"{key}. {value}")

    def run(self):
        while True:
            self.display()
            command = input().strip()
            if command == "0":
                return
            elif command == "1":
                print("Enter the size of a new maze")
                size = int(input())
                self.maze = Maze.create_maze(size, size)
                print(self.maze)
            elif command == "2":
                name = input()
                try:
                    self.maze = Maze.from_file(name)
                except FileNotFoundError:
                    print(f"The file {name} does not exist")
            elif self.maze is None:
                print("Incorrect option. Please try again")
                continue
            elif command == "3":
                name = input()
                self.maze.save_to_file(name)
            elif command == "4":
                print(self.maze)
            elif command == "5":
                self.maze.printable_solved_maze()
                print(self.maze)


if __name__ == "__main__":
    obj = Menu()
    obj.run()
