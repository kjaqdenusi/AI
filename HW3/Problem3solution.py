#######################################################
#### Problem 3 Solution
#### Author: Kenny A
#### Course: CSC 362 - Artificial Intelligence
#### Purpose: Implement Weighted A* with configurable alpha and beta
####          f(n) = α·g(n) + β·h(n)
####
#### this program allows experimentation with different weights
#### to see how they affect the A* algorithm's behavior.
#### - Higher beta biases toward goal (more greedy)
#### - Higher alpha biases toward shorter paths (more cautious)
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
# weighted A* maze solver
######################################################
class MazeGame:
    def __init__(self, root, maze, alpha=1.0, beta=1.0, x_offset=0, title="Weighted A*"):
        self.root = root
        self.maze = maze
        self.alpha = alpha  # weight for g(n)
        self.beta = beta    # weight for h(n)
        self.x_offset = x_offset

        self.rows = len(maze)
        self.cols = len(maze[0])

        self.agent_pos = (0, 0)                         # start state: (0,0) or top left
        self.goal_pos = (self.rows - 1, self.cols - 1)  # goal state: (rows-1, cols-1) or bottom right

        self.cells = [[Cell(x, y, maze[x][y] == 1) for y in range(self.cols)] for x in range(self.rows)]

        # start state's initial values
        self.cells[self.agent_pos[0]][self.agent_pos[1]].g = 0
        self.cells[self.agent_pos[0]][self.agent_pos[1]].h = self.heuristic(self.agent_pos)
        self.cells[self.agent_pos[0]][self.agent_pos[1]].f = self.beta * self.heuristic(self.agent_pos)

        self.cell_size = 40  # maze cell size in pixels
        self.canvas = None
        self.title = title
        self.path_length = 0


    def set_canvas(self, canvas):
        """Set the shared canvas for drawing"""
        self.canvas = canvas


    ############################################################
    #### draw the maze
    ############################################################
    def draw_maze(self):
        title_x = self.x_offset + (self.cols * self.cell_size) / 2  # center title above maze
        title_text = f"{self.title}\nα={self.alpha}, β={self.beta}"
        self.canvas.create_text(title_x, 25, font=("Arial", 11, "bold"), text=title_text)

        y_start = 50  # offset for title

        for x in range(self.rows):
            for y in range(self.cols):
                x_pos = self.x_offset + y * self.cell_size
                y_pos = y_start + x * self.cell_size

                color = 'maroon' if self.maze[x][y] == 1 else 'white'
                self.canvas.create_rectangle(
                    x_pos, y_pos,
                    x_pos + self.cell_size, y_pos + self.cell_size,
                    fill=color, outline='gray'
                )

                if not self.cells[x][y].is_wall:
                    g_val = self.cells[x][y].g if self.cells[x][y].g != float("inf") else "∞"
                    text = f'g={g_val}\nh={self.cells[x][y].h}'
                    self.canvas.create_text(
                        x_pos + self.cell_size/2,
                        y_pos + self.cell_size/2,
                        font=("Arial", 7), text=text
                    )


    ############################################################
    #### manhattan distance heuristic
    ############################################################
    def heuristic(self, pos):
        return abs(pos[0] - self.goal_pos[0]) + abs(pos[1] - self.goal_pos[1])


    ############################################################
    #### weighted A* algorithm: f(n) = α·g(n) + β·h(n)
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

            # agent goes E, W, N, and S, whenever possible
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_pos = (current_pos[0] + dx, current_pos[1] + dy)

                if 0 <= new_pos[0] < self.rows and 0 <= new_pos[1] < self.cols and not self.cells[new_pos[0]][new_pos[1]].is_wall:
                    new_g = current_cell.g + 1  # cost of moving to new position is 1 unit

                    if new_g < self.cells[new_pos[0]][new_pos[1]].g:
                        self.cells[new_pos[0]][new_pos[1]].g = new_g                # update the path cost g()
                        self.cells[new_pos[0]][new_pos[1]].h = self.heuristic(new_pos)  # update the heuristic h()

                        # weighted A*: f(n) = α·g(n) + β·h(n)
                        self.cells[new_pos[0]][new_pos[1]].f = (
                            self.alpha * new_g +
                            self.beta * self.cells[new_pos[0]][new_pos[1]].h
                        )

                        self.cells[new_pos[0]][new_pos[1]].parent = current_cell

                        # add the new cell to the priority queue
                        open_set.put((self.cells[new_pos[0]][new_pos[1]].f, new_pos))


    ############################################################
    #### reconstruct and display the optimal path
    ############################################################
    def reconstruct_path(self):
        current_cell = self.cells[self.goal_pos[0]][self.goal_pos[1]]
        self.path_length = 0
        y_start = 50

        while current_cell.parent:
            x, y = current_cell.x, current_cell.y
            x_pos = self.x_offset + y * self.cell_size
            y_pos = y_start + x * self.cell_size

            # draw path in skyblue
            self.canvas.create_rectangle(
                x_pos, y_pos,
                x_pos + self.cell_size, y_pos + self.cell_size,
                fill='skyblue', outline='gray'
            )

            # redraw cell with updated g() and h() values
            g_val = self.cells[x][y].g
            text = f'g={g_val}\nh={self.cells[x][y].h}'
            self.canvas.create_text(
                x_pos + self.cell_size/2,
                y_pos + self.cell_size/2,
                font=("Arial", 7), text=text
            )

            current_cell = current_cell.parent
            self.path_length += 1

        # display path length
        stats_x = self.x_offset + (self.cols * self.cell_size) / 2
        stats_y = y_start + self.rows * self.cell_size + 15
        self.canvas.create_text(
            stats_x, stats_y,
            font=("Arial", 9, "bold"),
            text=f"Path: {self.path_length}"
        )


############################################################
#### maze configuration
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
#### main program: test different alpha and beta values
############################################################
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Problem 3: Weighted A* - α and β Comparison")

    # create a large canvas to display multiple configurations
    canvas_width = 1200
    canvas_height = 700
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg='white')
    canvas.pack()

    # test different weight configurations
    # format: (alpha, beta, x_offset, y_offset, title)
    configurations = [
        (1.0, 1.0, 0, 0, "Standard A*"),           # top-left: normal A*
        (1.0, 2.0, 500, 0, "β=2 (Greedy)"),        # top-right: more greedy
        (0.0, 1.0, 0, 350, "α=0 (Pure Greedy)"),   # bottom-left: pure greedy
        (2.0, 1.0, 500, 350, "α=2 (Cautious)"),    # bottom-middle: more cautious
        (1.0, 0.5, 1000, 0, "β=0.5 (Conservative)") # right-top: less greedy
    ]

    games = []
    for alpha, beta, x_off, _, title in configurations:
        game = MazeGame(root, maze, alpha=alpha, beta=beta, x_offset=x_off, title=title)
        game.set_canvas(canvas)

        game.draw_maze()
        game.find_path()
        games.append(game)

    # add explanation text
    explanation = (
        "Weighted A*: f(n) = α·g(n) + β·h(n)\n"
        "α controls weight on actual cost, β controls weight on heuristic\n"
        "Higher β = more greedy (faster but may be suboptimal)\n"
        "Higher α = more cautious (optimal but slower)"
    )
    canvas.create_text(600, 680, font=("Arial", 10), text=explanation)

    root.mainloop()



# ---------------------------------------------------------------
# REFERENCES
# ---------------------------------------------------------------
# 1. variants of A* 
#    https://theory.stanford.edu/~amitp/GameProgramming/Variations.html
