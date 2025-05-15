from itertools import combinations
from pysat.solvers import Glucose3
import time
import copy
import sys
from multiprocessing import Process

# Doc du lieu tu tep, tra ve mang
def read_input(filename):
    grid = []
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            row = line.strip().split(", ")
            for i in range(len(row)):
                if row[i].isdigit():
                    row[i] = int(row[i])
            grid.append(row)
    return grid

# Ghi du lieu ra tep
def write_output(filename, grid):
    with open(filename, "w") as f:
        for row in grid:
            f.write(", ".join(map(str, row)) + "\n")  

# Tim o trong xung quanh mot vi tri
def find_empty_cells_around(grid, pos):
    empty_cells = []
    # Kiem tra cac vi tri xung quanh
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            # Bo qua vi tri chinh no
            if dx == 0 and dy == 0:
                continue
            neighbor = (pos[0] + dx, pos[1] + dy)
            if 0 <= neighbor[0] < len(grid) and 0 <= neighbor[1] < len(grid[neighbor[0]]):
                if grid[neighbor[0]][neighbor[1]] == "_":
                    empty_cells.append(neighbor)
    return empty_cells

# Tao tu dien cac o trong xung quanh cua moi vi tri co trong so
def find_empty_cells_around_dict(grid):
    empty_cells_dict = {}
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if type(grid[i][j]) == int:
                empty_cells = find_empty_cells_around(grid, (i, j))
                if empty_cells:
                    empty_cells_dict[(i, j)] = empty_cells
    return empty_cells_dict

# Ma hoa vi tri (i, j) thanh so nguyen
def encode_pos(pos, grid):
    return pos[0] * len(grid[0]) + pos[1] + 1 # tranh 0

# Phat sinh CNF
def generate_CNFs(grid):
    empty_cells_dict = find_empty_cells_around_dict(grid)
    CNFs = []
    for pos, empty_cells in empty_cells_dict.items():
        # Neu trong so = so o trong -> tat ca o trong deu la bay
        if len(empty_cells) == grid[pos[0]][pos[1]]:
            for empty_cell in empty_cells:
                CNFs.append([encode_pos(empty_cell, grid)])
        # To hop CNF
        else:
            """
            Gia su co k o trong xung quanh vi tri (i, j) va trong so = n (k > n)
            So luong Trap xung quanh vi tri (i, j) = n <==> so luong Gem xung quanh vi tri (i, j) = m (m = k - n)
            Can thoa man hai menh de:
            + n Trap -> m Gem : Voi moi to hop chap n + 1 cua k, luon co it nhat 1 Gem 
            + m Gem -> n Trap: Voi moi to hop chap m + 1 cua k, luon co it nhat 1 Trap
            """
            # CNF cho n Trap -> m Gem
            combinations_list = list(combinations(empty_cells, grid[pos[0]][pos[1]] + 1))
            for combination in combinations_list:
                CNFs.append([-encode_pos(empty_cell, grid) for empty_cell in combination])
            # CNF cho m Gem -> n Trap
            combinations_list = list(combinations(empty_cells, len(empty_cells) - grid[pos[0]][pos[1]] + 1))
            for combination in combinations_list:
                CNFs.append([encode_pos(empty_cell, grid) for empty_cell in combination])
    return CNFs

# Tra ve true khi so luong T xung quanh vi tri (i, j) khop voi trong so
def is_consistent(grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            # Voi moi o co trong so, neu so luong T xung quanh khong khop thi model khong phu hop
            if type(grid[i][j]) == int:
                # Dem so luong T xung quanh vi tri (i, j)
                num_traps = 0
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if dx == 0 and dy == 0:
                            continue
                        neighbor = (i + dx, j + dy)
                        if 0 <= neighbor[0] < len(grid) and 0 <= neighbor[1] < len(grid[neighbor[0]]):
                            if grid[neighbor[0]][neighbor[1]] == "T":
                                num_traps += 1
                empty_cells = find_empty_cells_around(grid, (i, j))
                if num_traps > grid[i][j] or num_traps + len(empty_cells) < grid[i][j]:
                    return False
    return True

# Tra ve mang cac vi tri o trong
def find_empty_cells(grid):
    empty_cells = []
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == "_":
                empty_cells.append((i, j))
    return empty_cells

def brute_force(grid):
    # Dem so o trong
    empty_cells = find_empty_cells(grid)
    # Su dung day bits de tao tat ca cac hoan vi
    bits = len(empty_cells)
    # Kiem tra tat ca cac hoan vi
    for bits in range(2 ** len(empty_cells)):
        for k in range(len(empty_cells)):
            # 1 la T, 0 la G
            if (bits >> k) & 1:
                grid[empty_cells[k][0]][empty_cells[k][1]] = "T"
            else:
                grid[empty_cells[k][0]][empty_cells[k][1]] = "G"
        # Kiem tra tinh hop le
        if is_consistent(grid):
            return True, grid
    return False, None


# De quy quay lui tim giai phap
def backtracking(grid, empty_cells, index):
    # Kiem tra khi da gan gia tri cho tat ca o trong
    if index == len(empty_cells):
        return is_consistent(grid), grid
    # Lay vi tri o trong
    i, j = empty_cells[index]
    # Gia su (i, j) la G    
    grid[i][j] = "G"
    if is_consistent(grid):
        result, solution = backtracking(grid, empty_cells, index + 1)
        if result:
            return True, solution
    # Gia su (i, j) la T
    grid[i][j] = "T"
    if is_consistent(grid):
        result, solution = backtracking(grid, empty_cells, index + 1)
        if result:
            return True, solution
    # Neu khong co giai phap, tra lai o trong
    grid[i][j] = "_"
    return False, None

def SAT_solver(grid):
    # Tao CNFs
    cnfs = generate_CNFs(grid)
    # Them cac menh de rang buoc
    solver = Glucose3()
    for cnf in cnfs:
        solver.add_clause(cnf)
    # Gan gia tri neu tim duoc solution
    if solver.solve():
        model = solver.get_model()
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == "_":
                    e = encode_pos((i, j), grid)
                    if e in model:
                        grid[i][j] = "T"
                    else:
                        grid[i][j] = "G"
        return True, grid
    return False, None

def run_algorithm(fi, fo):
    # Gioi han stack
    sys.setrecursionlimit(100000)
    
    # Doc du lieu tu tep vao mang
    grid = read_input(fi)
    
    # Bat dau thoi gian
    start_time = time.time()
    
    # # ---------------- PY-SAT ----------------
    # # Uncomment khoi nay de su dung pySAT
    # try:
    #     is_possible, solution = SAT_solver(grid)
    #     if is_possible:
    #         print(f"SAT SOLUTION FOUND\nEXECUTION TIME: {(time.time() - start_time):.10f}")
    #         write_output(fo, solution)
    #     else:
    #         print("NO SOLUTION WITH SAT\n")
    # except RecursionError:
    #     print(f"Thuat toan bi tran stack tai {(time.time() - start_time):.10f}.")
    #     return
    
    # # # ---------------- BRUTE FORCE ----------------
    # # Uncomment khoi nay de su dung Brute Force    
    # try:
    #     is_possible, solution = brute_force(grid)
    #     if is_possible:
    #         print(f"BRUTE FORCE SOLUTION FOUND\nEXECUTION TIME: {(time.time() - start_time):.10f}")
    #         write_output(fo, solution)
    #     else:
    #         print("NO SOLUTION WITH BRUTE FORCE\n")
    # except RecursionError:
    #     print(f"Thuat toan bi tran stack tai {(time.time() - start_time):.10f}.")
    #     return
    
    # ---------------- BACKTRACKING ----------------
    # Uncomment khoi nay de su dung Backtracking
    try:
        is_possible, solution = backtracking(grid, find_empty_cells(grid), 0)
        if is_possible:
            print(f"BACKTRACKING SOLUTION FOUND\nEXECUTION TIME: {(time.time() - start_time):.10f}")
            write_output(fo, solution)
        else:
            print("NO SOLUTION WITH BACKTRACKING\n")
    except RecursionError:
        print(f"Thuat toan bi tran stack tai {(time.time() - start_time):.10f}.")
        return

def main():
    # Gan ten tep
    fi = "input_2.txt" # de bai
    fo = "output_2.txt" # loi giai
    
    # Khoi tao process
    p = Process(target=run_algorithm, args=(fi, fo))
    p.start()
    p.join(timeout=120) # Thoi gian cho phep chay thuat toan

    if p.is_alive():
        p.terminate()
        print("RUNNING TIME TOO LONG. TIME OUT: 120s")
    else:
        print("RUN SUCCESSFULLY")

if __name__ == "__main__":
    main()