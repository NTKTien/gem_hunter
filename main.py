from itertools import combinations
from pysat.solvers import Glucose3

# Tim o trong xung quanh mot vi tri
def find_blanks(grid, i, j):
    blanks = []
    # Kiem tra cac vi tri xung quanh (i, j)
    for x in range(-1, 2):
        for y in range(-1, 2):
            # Bo qua vi tri chinh no
            if x == 0 and y == 0:
                continue
            ni, nj = i + x, j + y
            if 0 <= ni < len(grid) and 0 <= nj < len(grid[ni]):
                if grid[ni][nj] == "_":
                    blanks.append((ni, nj))
    return blanks

# Tim o trong xung quanh cac vi tri co trong so
def find_blank_dict(grid):
    blank_dict = {}
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if type(grid[i][j]) == int:
                blanks = find_blanks(grid, i, j)
                if blanks:
                    blank_dict[(i, j)] = blanks
    return blank_dict

# Ma hoa vi tri (i, j) thanh so nguyen
def encode_pos(pos, grid):
    return pos[0] * len(grid[0]) + pos[1] + 1 # tranh 0

# Phat sinh cac menh de hoi
def generate_CNFs(grid):
    blank_dict = find_blank_dict(grid)
    CNFs = []
    for pos, blanks in blank_dict.items():
        # Neu trong so = so o trong -> tat ca o trong deu la bay
        if len(blanks) == grid[pos[0]][pos[1]]:
            for blank_cell in blanks:
                CNFs.append([encode_pos(blank_cell, grid)])
        # To hop vi tri o trong -> bien doi CNF
        else:
            combinations_list = list(combinations(blanks, grid[pos[0]][pos[1]] + 1))
            for combination in combinations_list:
                CNFs.append([-encode_pos(blank_cell, grid) for blank_cell in combination])
    return CNFs

def main():
    # Doc ten tep
    filename = "input_1.txt"
    
    # Doc du lieu tu tep vao mang
    grid = []
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            row = line.strip().split(", ")
            for i in range(len(row)):
                if row[i].isdigit():
                    row[i] = int(row[i])
            grid.append(row)
    
    cnfs = generate_CNFs(grid)
    solver = Glucose3()
    for cnf in cnfs:
        solver.add_clause(cnf)
    if solver.solve():
        model = solver.get_model()
    else:
        print("NO SOLUTION")
        return
    
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == "_":
                e = encode_pos((i, j), grid)
                if e in model:
                    grid[i][j] = "T"
                else:
                    grid[i][j] = "G"
    
    # Ghi du lieu ra tep
    with open("output_1.txt", "w") as f:
        for row in grid:
            f.write(", ".join(map(str, row)) + "\n")
   

if __name__ == "__main__":
    main()