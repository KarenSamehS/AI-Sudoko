# 🧠 Sudoku Solver with GUI

![Gameplay](assets/Sudokogameplay.png)

A Python-based Sudoku solver and game built with **Tkinter**, featuring AI algorithms like **Backtracking**, **AC-3**, and heuristic enhancements. You can:
- Watch the AI solve puzzles
- Input your own puzzle
- Play random puzzles interactively

---

## 🎮 Features

- 🧩 **Mode 1:** Watch the AI solve a built-in puzzle step-by-step
- 🧠 **Mode 2:** Input your own puzzle and let the AI solve it
- 🎲 **Interactive Mode:** Play a randomly generated puzzle yourself
- ✅ Puzzle validation and solvability checks
- 👁️ Visual solving animation and updates

---

## 🧠 Algorithms Implemented

| Algorithm                 | Purpose                                           |
|--------------------------|---------------------------------------------------|
| **Backtracking**         | Puzzle solving & generation                       |
| **AC-3 (Arc Consistency)**| Domain pruning before solving                    |
| **MRV (Minimum Remaining Values)** | Smart variable selection        |
| **LCV (Least Constraining Value)** | Value selection heuristic       |
| **Forward Checking**     | Real-time domain reduction                        |

---

## 🧱 Data Structures

- **Board:** 9x9 grid of integers (`0` = empty)
- **Domains:** Set of valid values per cell
- **Arcs:** Related cell pairs used in AC-3
- **Queue:** Arc processing order

---

## 🖥️ GUI (Tkinter)

- Click-to-edit grid cells
- Real-time visualization of solving
- Input validation
- Random solvable puzzle generation
- Adjustable difficulty

---

## ⚡ Sample Run Stats

| Difficulty | AC-3 Time | Backtracking Steps |
|------------|-----------|--------------------|
| Easy       | 0.28 sec  | 0                  |
| Medium     | 2.16 sec  | 0                  |
| Hard       | 2.93 sec  | 0                  |

---

## 🚀 Getting Started

### ✅ Requirements

- Python 3.x
- Tkinter (comes built-in with Python)

### ▶️ Run the Program
```bash
python sudoku_gui.py
```

Replace `sudoku_gui.py` with the name of your main Python file.

---

## 📂 Project Structure

```
SudokuGame/
├── sudoku_gui.py
├── solver.py
├── utils.py
├── assets/
│   └── gameplay.png
├── README.md
└── .gitignore
```

---

## 📸 Gameplay Screenshot

> ![Gameplay](assets/gameplay.png)

Make sure the `assets/gameplay.png` file is committed in your repo so GitHub can render it.

---

## 📌 Future Work

- Add parallelization to solver
- Create web-based version
- Enhance difficulty classification
- Add hint system for players

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).
