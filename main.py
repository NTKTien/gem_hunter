from itertools import combinations
from pysat.solvers import Glucose3
import time
import copy

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
        # To hop CNF (chung minh trong bao cao)
        else:
            combinations_list = list(combinations(empty_cells, grid[pos[0]][pos[1]] + 1))
            for combination in combinations_list:
                CNFs.append([-encode_pos(empty_cell, grid) for empty_cell in combination])
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
    # Gia su (i, j) la T
    grid[i][j] = "T"
    if is_consistent(grid):
        result, solution = backtracking(grid, empty_cells, index + 1)
        if result:
            return True, solution
    # Gia su (i, j) la G    
    grid[i][j] = "G"
    if is_consistent(grid):
        result, solution = backtracking(grid, empty_cells, index + 1)
        if result:
            return True, solution
    # Neu khong co giai phap, tra lai o trong
    grid[i][j] = "_"
    return False, None

def main():
    # Gan ten tep
    fi = "input_1.txt" # de bai
    fo = "output_1.txt" # loi giai
    
    # Doc du lieu tu tep vao mang
    grid = read_input(fi)
    
    # Ghi nhan ket qua cac thuat toan
    solutions = {}
    execution_times = {}
    
    # Tao bang copy cho thuat toan pySAT
    pySAT_solution = copy.deepcopy(grid) # ban sao
    # Bat dau tinh thoi gian
    start_time = time.time()
    # Su dung thu vien pySAT
    # Tao CNFs
    cnfs = generate_CNFs(pySAT_solution)
    # Them cac menh de rang buoc
    solver = Glucose3()
    for cnf in cnfs:
        solver.add_clause(cnf)
    # Giai
    if solver.solve():
        model = solver.get_model()
        for i in range(len(pySAT_solution)):
            for j in range(len(pySAT_solution[0])):
                if pySAT_solution[i][j] == "_":
                    e = encode_pos((i, j), pySAT_solution)
                    if e in model:
                        pySAT_solution[i][j] = "T"
                    else:
                        pySAT_solution[i][j] = "G"
        solutions["PySAT"] = pySAT_solution
        print("SAT SOLUTION FOUND")
    else:
        solutions["PySAT"] = None
        print("NO SOLUTION WITH SAT")
    # Ket thuc tinh thoi gian
    end_time = time.time()
    execution_times["PySAT"] = end_time - start_time
          
    # Tao bang copy cho thuat toan brute force  
    brute_force_solution = copy.deepcopy(grid)
    # Bat dau tinh thoi gian
    start_time = time.time()
    # Su dung thuat toan brute force
    is_possible, brute_force_solution = brute_force(brute_force_solution)
    if is_possible:
        solutions["Brute Force"] = brute_force_solution
        print("BRUTE FORCE SOLUTION FOUND")
    else:
        solutions["Brute Force"] = None
        print("NO SOLUTION WITH BRUTE FORCE")
    # Ket thuc tinh thoi gian
    end_time = time.time()
    execution_times["Brute Force"] = end_time - start_time
    
    # Tao bang copy cho thuat toan backtracking
    backtracking_solution = copy.deepcopy(grid)
    # Bat dau tinh thoi gian
    start_time = time.time()
    # Su dung thuat toan backtracking              
    is_possible, backtracking_solution = backtracking(backtracking_solution, find_empty_cells(backtracking_solution), 0)
    if is_possible:
        solutions["Backtracking"] = backtracking_solution
        print("BACKTRACKING SOLUTION FOUND")
    else:
        solutions["Backtracking"] = None
        print("NO SOLUTION WITH BACKTRACKING")
    # Ket thuc tinh thoi gian
    end_time = time.time()
    execution_times["Backtracking"] = end_time - start_time
        
    # Ghi tat ca ket qua ra tep
    with open(fo, "w") as f:
        for algorithm, solution in solutions.items():
            if solution:
                f.write(f"{algorithm} solution:\n")
                for row in solution:
                    f.write(", ".join(map(str, row)) + "\n")
                f.write(f"execution_time: {execution_times[algorithm]:.10f}\n\n")
            else:
                f.write(f"{algorithm} NO SOLUTION\n\n")
                
    print("RESULTS ARE SUCCESSFULLY WRITTEN TO FILE\n")  

if __name__ == "__main__":
    main()