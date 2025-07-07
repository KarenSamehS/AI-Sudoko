import tkinter as tk
from tkinter import messagebox
import time
import copy
import random
from collections import defaultdict
import Arc_Consistency
import logging

# easy mode ranges from (10-35) , medium mode ranges from (35-50) , hard mode (50 - 55)
no_of_removals = 50
filename = "log.txt"

logging.basicConfig(filename=filename, level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Sudoku Solver with Heuristics")
        self.cells = {}
        self.original_board = None
        self.solving = False
        self.heuristic = "MRV"  # Default heuristic
        self.removed_once = False
        self.backtracking_steps = 0
        with open(filename, "w") as f:
            pass
        f.close()

        # Initialize empty board
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.domains = None  # For Forward Checking

        try:
            self.create_gui()
            self.generate_board()  # Generate a random valid board
            self.original_board = copy.deepcopy(self.board)
        except Exception as e:
            print(f"Error in initialization: {e}")
            logging.error(f"Error in initialization: {e}")
            raise

    def create_gui(self):
        # Create main frame for grid
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)
        # Create 9x9 grid inside 3x3 sub grids
        for box_row in range(3):
            for box_col in range(3):
                # Create a frame for each 3x3 subgrid with a border
                subframe = tk.Frame(
                    self.frame,
                    highlightbackground="black",
                    highlightthickness=2  # Border thickness
                )
                subframe.grid(row=box_row, column=box_col, padx=0, pady=0, sticky="nsew")

                # Fill the subframe with 3x3 Entry widgets
                for i in range(3):
                    for j in range(3):
                        cell = tk.Entry(
                            subframe,
                            width=3,
                            font=('Arial', 18),
                            justify='center'
                        )
                        cell.grid(row=i, column=j, padx=1, pady=1)
                        self.cells[(box_row * 3 + i, box_col * 3 + j)] = cell

        # Create control frame for buttons and heuristic selection
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # Heuristic selection
        tk.Label(control_frame, text="Heuristic:", font=('Arial', 12)).pack(side=tk.LEFT, padx=5)
        self.heuristic_var = tk.StringVar(value="MRV")
        heuristic_menu = tk.OptionMenu(control_frame, self.heuristic_var, "MRV", "Forward Checking", "LCV", "ALL",
                                       "AC-3",
                                       command=self.set_heuristic)
        heuristic_menu.pack(side=tk.LEFT, padx=5)

        # Buttons
        tk.Button(control_frame, text="Generate New Board", command=self.generate_board).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Remove Numbers", command=self.remove_numbers).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Solve", command=self.solve_puzzle).pack(side=tk.LEFT, padx=5)
        self.mode_var = tk.StringVar(value="Mode 1")
        mode_menu = tk.OptionMenu(control_frame, self.mode_var, "Mode 1", "Mode 2", "Interactive",
                                  command=self.change_input_mode)
        mode_menu.pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Reset", command=self.reset_board).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Submit", command=self.get_input_board).pack(side=tk.LEFT, padx=5)

    def change_input_mode(self, value):
        self.mode = value
        print(self.mode)
        logging.info(f"Mode changed to: {self.mode}")
        if self.mode == "Mode 2":
            for r in range(9):
                for c in range(9):
                    self.board[r][c] = 0
            self.domains = None
            self.update_gui()
            self.original_board = copy.deepcopy(self.board)
        elif self.mode == "Interactive":
            self.generate_board()
            self.remove_numbers()
        else:
            self.generate_board()

    def is_user_input_solvable(self):
        # Backup current board
        current_board = copy.deepcopy(self.board)
        self.solving = True
        solvable = self.solve()
        self.solving = False
        self.board = current_board
        self.update_gui()
        return solvable

    def set_heuristic(self, value):
        """Update the selected heuristic."""
        self.heuristic = value
        logging.info(f"Heuristic set to: {self.heuristic}")


    def update_gui(self):
        """Update the GUI to reflect the current board state."""
        for i in range(9):
            for j in range(9):
                self.cells[(i, j)].config(state='normal')
                self.cells[(i, j)].delete(0, tk.END)
                if self.board[i][j] != 0:
                    self.cells[(i, j)].insert(0, str(self.board[i][j]))
                    self.cells[(i, j)].config(state='disabled')
                else:
                    self.cells[(i, j)].config(state='normal')

    def reset_board(self):
        """Reset the board to the initial state."""
        try:
            self.board = copy.deepcopy(self.original_board)
            self.solving = False
            self.domains = None
            self.backtracking_steps = 0
            with open(filename, "w") as f:
                pass
            f.close()
            self.update_gui()
            logging.info("Board reset to the initial state")
        except Exception as e:
            print(f"Error in reset_board: {e}")
            logging.error(f"Error in reset_board: {e}")

        

    def is_valid(self, num, pos):
        """Check if placing num at pos is valid."""
        row, col = pos
        # Check row
        for j in range(9):
            if self.board[row][j] == num and col != j:
                return False
        # Check column
        for i in range(9):
            if self.board[i][col] == num and row != i:
                return False
        # Check 3x3 box
        box_x = col // 3
        box_y = row // 3
        for i in range(box_y * 3, box_y * 3 + 3):
            for j in range(box_x * 3, box_x * 3 + 3):
                if self.board[i][j] == num and (i, j) != pos:
                    return False
        return True

    def get_possible_values(self, pos):
        """Return list of valid values for a given position."""
        if self.board[pos[0]][pos[1]] != 0:
            return []
        possible = []
        for num in range(1, 10):
            if self.is_valid(num, pos):
                possible.append(num)
        return possible

    def initialize_domains(self):
        """Initialize domains for Forward Checking."""
        self.domains = defaultdict(list)
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    self.domains[(i, j)] = self.get_possible_values((i, j))
                else:
                    self.domains[(i, j)] = [self.board[i][j]]

    def find_empty_mrv(self):
        """Find the empty cell with the minimum remaining values (MRV)."""
        min_values = 10  # More than possible (1-9)
        best_cell = None
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    if self.heuristic in ("ALL", "AC-3", "Forward Checking"):
                        possible = len(self.domains[(i, j)])
                    else:
                        possible = len(self.get_possible_values((i, j)))
                    if possible < min_values:
                        min_values = possible
                        best_cell = (i, j)
                    if possible == 1:
                        return best_cell
        return best_cell

    def get_lcv_values(self, pos):
        """Sort values for pos based on Least Constraining Value (LCV)."""
        row, col = pos
        value_counts = []
        fc = False

        if self.heuristic in ("ALL", "AC-3", "Forward Checking"):
            possible = self.domains[(row, col)]
            fc = True
        else:
            possible = self.get_possible_values((row, col))

        for num in possible:
            count = 0
            # Check related cells (row, column, box)
            for j in range(9):
                if self.board[row][j] == 0 and (row, j) != pos:
                    if num in (
                            self.domains[
                                (row, j)] if fc else self.get_possible_values(
                                (row, j))):
                        count += 1
            for i in range(9):
                if self.board[i][col] == 0 and (i, col) != pos:
                    if num in (
                            self.domains[
                                (i, col)] if fc else self.get_possible_values(
                                (i, col))):
                        count += 1
            box_x = col // 3
            box_y = row // 3
            for i in range(box_y * 3, box_y * 3 + 3):
                for j in range(box_x * 3, box_x * 3 + 3):
                    if self.board[i][j] == 0 and (i, j) != pos:
                        if num in (
                                self.domains[
                                    (i, j)] if fc else self.get_possible_values(
                                    (i, j))):
                            count += 1
            value_counts.append((count, num))

        # Sort by count (ascending) to get the least constraining values first
        value_counts.sort()
        return [num for _, num in value_counts]

    def update_domains(self, pos, value):
        """Update domains for Forward Checking after assigning value to pos."""
        row, col = pos
        affected_cells = []

        # Update row
        for j in range(9):
            if self.board[row][j] == 0 and (row, j) != pos:
                if value in self.domains[(row, j)]:
                    self.domains[(row, j)].remove(value)
                    affected_cells.append((row, j))

        # Update column
        for i in range(9):
            if self.board[i][col] == 0 and (i, col) != pos:
                if value in self.domains[(i, col)]:
                    self.domains[(i, col)].remove(value)
                    affected_cells.append((i, col))

        # Update 3x3 box
        box_x = col // 3
        box_y = row // 3
        for i in range(box_y * 3, box_y * 3 + 3):
            for j in range(box_x * 3, box_x * 3 + 3):
                if self.board[i][j] == 0 and (i, j) != pos:
                    if value in self.domains[(i, j)]:
                        self.domains[(i, j)].remove(value)
                        affected_cells.append((i, j))

        return affected_cells

    def restore_domains(self, affected_cells, value):
        """Restore domains for Forward Checking when backtracking."""
        for pos in affected_cells:
            if value not in self.domains[pos]:
                self.domains[pos].append(value)

    def generate_board(self):
        """Generate a random valid Sudoku board using backtracking with MRV."""
        try:
            # Clear the board
            self.board = [[0 for _ in range(9)] for _ in range(9)]
            self.domains = None

            def fill_board():
                empty = self.find_empty_mrv()
                if not empty:
                    return True
                row, col = empty

                values = list(range(1, 10))
                random.shuffle(values)  # Randomize value order
                for num in values:
                    if self.is_valid(num, (row, col)):
                        self.board[row][col] = num
                        if fill_board():
                            return True
                        self.board[row][col] = 0
                return False

            if fill_board():
                self.original_board = copy.deepcopy(self.board)
                self.update_gui()
                self.removed_once = False

                print("Generated a new random Sudoku board")
                logging.info("Generated a new random Sudoku board")
           
            else:
                print("Error: Failed to generate a valid Sudoku board")
                logging.error("Error: Failed to generate a valid Sudoku board")
               
                messagebox.showerror("Sudoku Generator", "Failed to generate a valid board!")
        except Exception as e:
            print(f"Error in generate_board: {e}")
            logging.error(f"Error in generate_board: {e}")


    def remove_numbers(self):
        """Remove exactly 43 numbers ensuring the puzzle has a unique solution."""
        if self.removed_once:
            messagebox.showwarning("Warning", "Numbers can only be removed once per generated board.")
            logging.warning("Attempted to remove numbers again, but numbers can only be removed once per generated board.")
            
            return

        def has_unique_solution(board):
            solutions = []

            def count_solutions():
                empty = self.find_empty_mrv()
                if not empty:
                    solutions.append(1)
                    return len(solutions) <= 1
                row_, col_ = empty
                for num in self.get_possible_values((row_, col_)):
                    if self.is_valid(num, (row_, col_)):
                        board[row_][col_] = num
                        if not count_solutions():
                            return False
                        board[row_][col_] = 0
                return True

            return count_solutions() and len(solutions) == 1

        def try_removal(board, count):
            positions = [(i, j) for i in range(9) for j in range(9)]
            random.shuffle(positions)
            removed = 0

            for row, col in positions:
                if removed == count:
                    break
                temp = board[row][col]
                board[row][col] = 0
                if has_unique_solution(copy.deepcopy(board)):
                    removed += 1
                else:
                    board[row][col] = temp

            return removed == count, board

        # Keep trying until we get a board with exactly 43 removable cells
        while True:
            board_copy = copy.deepcopy(self.original_board)
            success, new_board = try_removal(board_copy, count=no_of_removals)
            if success:
                self.board = new_board
                break

        self.removed_once = True
        self.original_board = copy.deepcopy(self.board)
        self.update_gui()
        print(f"Exactly {no_of_removals} numbers removed")
        logging.info(f"Successfully removed {no_of_removals} numbers from the board")
                

    def solve_ALL(self):
        """Solve using MRV + LCV + Forward Checking (combined heuristics)."""
        try:
            if not self.solving:
                return False

            # Initialize domains once
            if self.domains is None and self.heuristic != "AC-3":
                self.initialize_domains()

            # MRV: Find the cell with the smallest domain (most constrained)
            cell = self.find_empty_mrv()
            if not cell:
                return True  # Solved

            row, col = cell

            # LCV: Order values to try least-constraining first
            possible_values = self.get_lcv_values(cell)

            for num in possible_values:
                # FC: Update domains and track changes
                affected_cells = self.update_domains(cell, num)

                # FC: Check for domain wipe-out (inconsistency)
                if not all(len(self.domains[(i, j)]) > 0
                           for i in range(9) for j in range(9)
                           if self.board[i][j] == 0):
                    self.restore_domains(affected_cells, num)
                    continue

                # Assign value
                self.board[row][col] = num
                self.cells[(row, col)].delete(0, tk.END)
                self.cells[(row, col)].insert(0, str(num))
                self.cells[(row, col)].config(fg='blue')
                self.root.update()
                time.sleep(0.05)

                # Recurse with all heuristics still active
                if self.solve_ALL():
                    return True

                # Backtrack
                print(f"Backtracking from cell ({row},{col}), value {num}")
                logging.info(f"Backtracking from cell ({row},{col}), value {num}")
                self.board[row][col] = 0
                self.backtracking_steps += 1
                self.cells[(row, col)].delete(0, tk.END)
                self.cells[(row, col)].config(fg='black')
                self.root.update()
                time.sleep(0.05)

                # FC: Undo domain pruning
                self.restore_domains(affected_cells, num)

            return False

        except Exception as e:
            print(f"Error in solve_ALL: {e}")
            return False

    def solve(self):
        """Solve the Sudoku puzzle using selected heuristic."""
        try:
            if not self.solving:
                return False

            # Initialize domains for Forward Checking
            if self.heuristic == "Forward Checking" and self.domains is None:
                self.initialize_domains()

            empty = self.find_empty_mrv()
            if not empty:
                return True
            row, col = empty

            # Get values to try (LCV or default order)
            possible_values = self.get_lcv_values((row, col)) if self.heuristic == "LCV" else \
                (self.domains[(row, col)] if self.heuristic == "Forward Checking" else self.get_possible_values(
                    (row, col)))

            for num in possible_values:
                print(f"Assigning value {num} to cell ({row},{col})")
                logging.info(f"Assigning value {num} to cell ({row},{col})")
                if self.heuristic == "Forward Checking":
                    # Check if assignment leads to empty domains
                    affected_cells = self.update_domains((row, col), num)
                    valid = True
                    for i in range(9):
                        for j in range(9):
                            if self.board[i][j] == 0 and len(self.domains[(i, j)]) == 0:
                                valid = False
                                break
                        if not valid:
                            break
                    if not valid:
                        self.restore_domains(affected_cells, num)
                        continue

                self.board[row][col] = num
                self.cells[(row, col)].delete(0, tk.END)
                self.cells[(row, col)].insert(0, str(num))
                self.cells[(row, col)].config(fg='blue')
                self.root.update()
                time.sleep(0.05)  # Delay for visual effect

                if self.solve():
                    return True

                print(f"Backtracking from cell ({row},{col}), value {num}")
                logging.info(f"Backtracking from cell ({row},{col}), value {num}")
                self.board[row][col] = 0
                self.backtracking_steps += 1
                self.cells[(row, col)].delete(0, tk.END)
                self.cells[(row, col)].config(fg='black')
                self.root.update()
                time.sleep(0.05)

                if self.heuristic == "Forward Checking":
                    self.restore_domains(affected_cells, num)

            return False
        except Exception as e:
            print(f"Error in solve: {e}")
            return False

    def solve_puzzle(self):
        """Start the solving process."""
        if self.solving:
            return
        try:
            self.solving = True
            self.domains = None  # Reset domains
            start_time = time.time()
            if self.heuristic == "ALL":
                solved = self.solve_ALL()
            elif self.heuristic == "AC-3":
                solved = self.solve_ac3()
            else:
                solved = self.solve()

            if solved:
                self.solving = False
                elapsed = time.time() - start_time
                print(
                    f"Heuristic {self.heuristic} took {elapsed:.3f} seconds and number of backtracking steps = {self.backtracking_steps}")
                logging.info(
                    f"Heuristic {self.heuristic} took {elapsed:.3f} seconds and number of backtracking steps = {self.backtracking_steps}")
                messagebox.showinfo("Sudoku Solver", f"Puzzle solved successfully with {self.heuristic}!")
            else:
                self.solving = False
                elapsed = time.time() - start_time
                print(
                    f"Heuristic {self.heuristic} took {elapsed:.3f} seconds and number of backtracking steps = {self.backtracking_steps}")
                logging.info( f"Heuristic {self.heuristic} took {elapsed:.3f} seconds and number of backtracking steps = {self.backtracking_steps}")
                messagebox.showerror("Sudoku Solver", "No solution exists!")
        except Exception as e:
            print(f"Error in solve_puzzle: {e}")
            self.solving = False

    def get_input_board(self):
        full = True
        for i in range(9):
            for j in range(9):
                try:
                    value = self.cells[(i, j)].get().strip()
                    if value:
                        num = int(value)
                        if self.is_valid(num, (i, j)) and 1 <= num <= 9:
                            self.board[i][j] = num
                        else:
                            raise ValueError(f"Invalid number {num} at ({i},{j})")
                    else:
                        full = False
                except ValueError:
                    if self.cells[(i, j)].get() != "":
                        messagebox.showerror("Invalid Input",
                                             f"Invalid value at cell ({i},{j}).")
                    return None
        if full:
            messagebox.showinfo(title="Success", message="You have solved the sudoku ;)")
        self.original_board = copy.deepcopy(self.board)
        self.update_gui()
        self.removed_once = False

    def solve_ac3(self):
        dom = Arc_Consistency.initialize_domains(self.board)
        pruned_dom = Arc_Consistency.ac3(self.board, dom, Arc_Consistency.define_arcs(self.board), filename=filename)
        if not pruned_dom:
            messagebox.showerror("Sudoku Solver", "AC-3 failed")
            return

        # Convert domain to dictionary format for use in solver
        # Convert 2D list to dictionary with (i, j) keys
        self.domains = defaultdict(list)
        for i in range(9):
            for j in range(9):
                self.domains[(i, j)] = list(pruned_dom[i][j])

        return self.solve_ALL()

    def run(self):
        """Start the main loop."""
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    app.run()
