#######################################################
#### Problem 1 Solution
#### Author: Kenny A
#### Course: CSC 362 - Artificial Intelligence
#### Purpose: Compare A* and Greedy Best First Search algorithms
####          to demonstrate differences in pathfinding behavior
####
#### this program modifies AStarMaze to run both A* and greedy
####  best first side by side to show how different evaluation
#### functions produce different paths.
#######################################################

import tkinter as tk
from queue import PriorityQueue


######################################################
#### a cell stores f(), g() and h() values
#### a cell is either open or part of a wall
######################################################
class Cell:
    def __init__(self, x, y, is_wall=False):
        self.x = x
        self.y = y
        self.is_wall = is_wall
        self.g = float("inf")
        self.h = 0
        self.f = float("inf")
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f


######################################################
# maze solver that can use either A* or Greedy Best-First
######################################################
class MazeGame:
    def __init__(self, root, maze, algorithm="astar", x_offset=0, title="Maze"):
        self.root = root
        self.maze = maze
        self.algorithm = algorithm  # "astar" or "greedy"
        self.x_offset = x_offset    # for side-by-side display

        self.rows = len(maze)
        self.cols = len(maze[0])

        self.agent_pos = (0, 0)                         # start state: (0,0) or top left
        self.goal_pos = (self.rows - 1, self.cols - 1)  # goal state: (rows-1, cols-1) or bottom right

        self.cells = [[Cell(x, y, maze[x][y] == 1) for y in range(self.cols)] for x in range(self.rows)]

        # start state's initial values for f(n) = g(n) + h(n)
        self.cells[self.agent_pos[0]][self.agent_pos[1]].g = 0
        self.cells[self.agent_pos[0]][self.agent_pos[1]].h = self.heuristic(self.agent_pos)
        self.cells[self.agent_pos[0]][self.agent_pos[1]].f = self.heuristic(self.agent_pos)

        self.cell_size = 50      # maze cell size in pixels
        self.canvas = None
        self.title = title


    def set_canvas(self, canvas):
        """Set the shared canvas for drawing"""
        self.canvas = canvas


    ############################################################
    #### draw the maze on the canvas
    ############################################################
    def draw_maze(self):
        title_x = self.x_offset + (self.cols * self.cell_size) / 2  # center title above maze
        self.canvas.create_text(title_x, 20, font=("Arial", 16, "bold"), text=self.title)

        for x in range(self.rows):
            for y in range(self.cols):
                x_pos = self.x_offset + y * self.cell_size
                y_pos = 40 + x * self.cell_size  # offset for title

                color = 'maroon' if self.maze[x][y] == 1 else 'white'
                self.canvas.create_rectangle(
                    x_pos, y_pos,
                    x_pos + self.cell_size, y_pos + self.cell_size,
                    fill=color, outline='black'
                )

                if not self.cells[x][y].is_wall:
                    g_val = self.cells[x][y].g if self.cells[x][y].g != float("inf") else "∞"
                    text = f'g={g_val}\nh={self.cells[x][y].h}'
                    self.canvas.create_text(
                        x_pos + self.cell_size/2,
                        y_pos + self.cell_size/2,
                        font=("Arial", 8), text=text
                    )


    ############################################################
    #### manhattan distance heuristic
    ############################################################
    def heuristic(self, pos):
        return abs(pos[0] - self.goal_pos[0]) + abs(pos[1] - self.goal_pos[1])


    ############################################################
    #### pathfinding algorithm (A* or greedy best first)
    ############################################################
    def find_path(self):
        open_set = PriorityQueue()

        # add the start state to the queue
        if self.algorithm == "greedy":
            # greedy best-first: f(n) = h(n) only
            open_set.put((self.cells[self.agent_pos[0]][self.agent_pos[1]].h, self.agent_pos))
        else:
            # A*: f(n) = g(n) + h(n)
            open_set.put((0, self.agent_pos))

        # continue exploring until the queue is exhausted
        while not open_set.empty():
            _, current_pos = open_set.get()
            current_cell = self.cells[current_pos[0]][current_pos[1]]

            if current_pos == self.goal_pos:  # stop if goal is reached
                self.reconstruct_path()
                break

            # agent goes E, W, N, and S, whenever possible
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_pos = (current_pos[0] + dx, current_pos[1] + dy)

                if 0 <= new_pos[0] < self.rows and 0 <= new_pos[1] < self.cols and not self.cells[new_pos[0]][new_pos[1]].is_wall:
                    new_g = current_cell.g + 1  # cost of moving to new position is 1 unit

                    if new_g < self.cells[new_pos[0]][new_pos[1]].g:
                        self.cells[new_pos[0]][new_pos[1]].g = new_g              # update the path cost g()
                        self.cells[new_pos[0]][new_pos[1]].h = self.heuristic(new_pos)  # update the heuristic h()

                        # update the evaluation function
                        if self.algorithm == "greedy":
                            self.cells[new_pos[0]][new_pos[1]].f = self.cells[new_pos[0]][new_pos[1]].h  # greedy: f(n) = h(n)
                        else:
                            self.cells[new_pos[0]][new_pos[1]].f = new_g + self.cells[new_pos[0]][new_pos[1]].h  # A*: f(n) = g(n) + h(n)

                        self.cells[new_pos[0]][new_pos[1]].parent = current_cell

                        # add the new cell to the priority queue
                        open_set.put((self.cells[new_pos[0]][new_pos[1]].f, new_pos))


    ############################################################
    #### reconstruct and draw the optimal path
    ############################################################
    def reconstruct_path(self):
        current_cell = self.cells[self.goal_pos[0]][self.goal_pos[1]]
        path_length = 0

        while current_cell.parent:
            x, y = current_cell.x, current_cell.y
            x_pos = self.x_offset + y * self.cell_size
            y_pos = 40 + x * self.cell_size

            # draw path in skyblue
            self.canvas.create_rectangle(
                x_pos, y_pos,
                x_pos + self.cell_size, y_pos + self.cell_size,
                fill='skyblue', outline='black'
            )

            # redraw cell with updated g() and h() values
            g_val = self.cells[x][y].g
            text = f'g={g_val}\nh={self.cells[x][y].h}'
            self.canvas.create_text(
                x_pos + self.cell_size/2,
                y_pos + self.cell_size/2,
                font=("Arial", 8), text=text
            )

            current_cell = current_cell.parent
            path_length += 1

        # display path length
        stats_x = self.x_offset + (self.cols * self.cell_size) / 2
        stats_y = 40 + self.rows * self.cell_size + 20
        self.canvas.create_text(
            stats_x, stats_y,
            text=f"Path Length: {path_length}"
        )


############################################################
#### modified maze to show difference between algorithms
#### this maze creates scenarios where greedy and A* differ
############################################################
maze = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
]


############################################################
#### main program: create side by side comparison
############################################################
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Problem 1: A* vs Greedy Best-First Comparison")

    # create shared canvas for both algorithms
    canvas_width = 1000
    canvas_height = 600
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg='white')
    canvas.pack()

    # create greedy best-first solver (left side)
    greedy_game = MazeGame(root, maze, algorithm="greedy", x_offset=0, title="Greedy Best-First")
    greedy_game.set_canvas(canvas)
    greedy_game.draw_maze()
    greedy_game.find_path()

    # create A* solver (right side)
    astar_game = MazeGame(root, maze, algorithm="astar", x_offset=500, title="A* Search")
    astar_game.set_canvas(canvas)
    astar_game.draw_maze()
    astar_game.find_path()

    root.mainloop()


# ---------------------------------------------------------------
# REFERENCES
# ---------------------------------------------------------------
# 1. introduction to A* :
#    http://theory.stanford.edu/~amitp/GameProgramming/AStarComparison.html