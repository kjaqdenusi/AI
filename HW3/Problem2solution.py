#######################################################
#### Problem 2 Solution
#### Author: Kenny A
#### Course: CSC 362 - Artificial Intelligence
#### Purpose: Implement A* with Euclidean distance heuristic
####          and diagonal movement (8-directional)
####
#### this program modifies AStarMaze to:
#### - use euclidean distance instead of manhattan distance
#### - allow diagonal moves (NE, NW, SE, SW) in addition to cardinal moves
#### - randomize move order for exploration
#######################################################

import tkinter as tk
from queue import PriorityQueue
import math
import random


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
# maze solver with euclidean distance and diagonal moves
######################################################
class MazeGame:
    def __init__(self, root, maze):
        self.root = root
        self.maze = maze

        self.rows = len(maze)
        self.cols = len(maze[0])

        self.agent_pos = (0, 0)                         # start state: (0,0) or top left
        self.goal_pos = (self.rows - 1, self.cols - 1)  # goal state: (rows-1, cols-1) or bottom right

        self.cells = [[Cell(x, y, maze[x][y] == 1) for y in range(self.cols)] for x in range(self.rows)]

        # start state's initial values for f(n) = g(n) + h(n)
        self.cells[self.agent_pos[0]][self.agent_pos[1]].g = 0
        self.cells[self.agent_pos[0]][self.agent_pos[1]].h = self.heuristic(self.agent_pos)
        self.cells[self.agent_pos[0]][self.agent_pos[1]].f = self.heuristic(self.agent_pos)

        self.cell_size = 60  # maze cell size in pixels
        self.canvas = tk.Canvas(root, width=self.cols * self.cell_size, height=self.rows * self.cell_size + 50, bg='white')
        self.canvas.pack()

        self.draw_maze()
        self.find_path()  # display the optimum path in the maze


    ############################################################
    #### draw the maze
    ############################################################
    def draw_maze(self):
        for x in range(self.rows):
            for y in range(self.cols):
                color = 'maroon' if self.maze[x][y] == 1 else 'white'
                self.canvas.create_rectangle(
                    y * self.cell_size, x * self.cell_size,
                    (y + 1) * self.cell_size, (x + 1) * self.cell_size,
                    fill=color, outline='black'
                )

                if not self.cells[x][y].is_wall:
                    g_val = self.cells[x][y].g if self.cells[x][y].g != float("inf") else "∞"
                    h_val = f"{self.cells[x][y].h:.1f}" if self.cells[x][y].h != 0 else "0"
                    text = f'g={g_val}\nh={h_val}'
                    self.canvas.create_text(
                        (y + 0.5) * self.cell_size,
                        (x + 0.5) * self.cell_size,
                        font=("Arial", 9), text=text
                    )


    ############################################################
    #### euclidean distance heuristic
    #### sqrt((x1-x2)^2 + (y1-y2)^2)
    ############################################################
    def heuristic(self, pos):
        dx = abs(pos[0] - self.goal_pos[0])
        dy = abs(pos[1] - self.goal_pos[1])
        return math.sqrt(dx * dx + dy * dy)


    ############################################################
    #### A* algorithm with 8-directional movement
    ############################################################
    def find_path(self):
        open_set = PriorityQueue()
        open_set.put((0, self.agent_pos))  # add the start state to the queue

        # continue exploring until the queue is exhausted
        while not open_set.empty():
            _, current_pos = open_set.get()
            current_cell = self.cells[current_pos[0]][current_pos[1]]

            if current_pos == self.goal_pos:  # stop if goal is reached
                self.reconstruct_path()
                break

            # 8-directional movement: N, S, E, W, NE, NW, SE, SW
            # cardinal directions have cost 1, diagonal moves have cost sqrt(2)
            moves = [
                (0, 1, 1),                 # E
                (0, -1, 1),                # W
                (1, 0, 1),                 # S
                (-1, 0, 1),                # N
                (-1, 1, math.sqrt(2)),     # NE
                (-1, -1, math.sqrt(2)),    # NW
                (1, 1, math.sqrt(2)),      # SE
                (1, -1, math.sqrt(2))      # SW
            ]

            random.shuffle(moves)  # randomize move order as required by assignment

            for dx, dy, cost in moves:
                new_pos = (current_pos[0] + dx, current_pos[1] + dy)

                if 0 <= new_pos[0] < self.rows and 0 <= new_pos[1] < self.cols and not self.cells[new_pos[0]][new_pos[1]].is_wall:
                    new_g = current_cell.g + cost  # cost depends on direction (1 for cardinal, sqrt(2) for diagonal)

                    if new_g < self.cells[new_pos[0]][new_pos[1]].g:
                        self.cells[new_pos[0]][new_pos[1]].g = new_g                # update the path cost g()
                        self.cells[new_pos[0]][new_pos[1]].h = self.heuristic(new_pos)  # update the heuristic h()
                        self.cells[new_pos[0]][new_pos[1]].f = new_g + self.cells[new_pos[0]][new_pos[1]].h  # f(n) = g(n) + h(n)
                        self.cells[new_pos[0]][new_pos[1]].parent = current_cell

                        # add the new cell to the priority queue
                        open_set.put((self.cells[new_pos[0]][new_pos[1]].f, new_pos))


    ############################################################
    #### reconstruct and display the optimal path
    ############################################################
    def reconstruct_path(self):
        current_cell = self.cells[self.goal_pos[0]][self.goal_pos[1]]
        path_length = 0
        total_cost = current_cell.g

        while current_cell.parent:
            x, y = current_cell.x, current_cell.y

            # draw path in skyblue
            self.canvas.create_rectangle(
                y * self.cell_size, x * self.cell_size,
                (y + 1) * self.cell_size, (x + 1) * self.cell_size,
                fill='skyblue', outline='black'
            )

            # redraw cell with updated g() and h() values
            g_val = f"{self.cells[x][y].g:.2f}"
            h_val = f"{self.cells[x][y].h:.1f}"
            text = f'g={g_val}\nh={h_val}'
            self.canvas.create_text(
                (y + 0.5) * self.cell_size,
                (x + 0.5) * self.cell_size,
                font=("Arial", 8), text=text
            )

            current_cell = current_cell.parent
            path_length += 1

        # display path statistics
        stats_text = f"Path Length: {path_length} steps | Total Cost: {total_cost:.2f}"
        self.canvas.create_text(
            (self.cols * self.cell_size) / 2,
            self.rows * self.cell_size + 25,
            font=("Arial", 12, "bold"),
            text=stats_text
        )


############################################################
#### maze configuration for testing diagonal movement
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
#### main program
############################################################
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Problem 2: A* with Euclidean Distance and Diagonal Movement")

    game = MazeGame(root, maze)

    root.mainloop()


# ---------------------------------------------------------------
# REFERENCES
# ---------------------------------------------------------------
# 1. heuristics for grid based pathfinding :
#    http://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html
