import random
import copy

# Tra ve ngau nhien T, G hoac trong so
def random_element():
    values = ['T', 'G', 'x']
    probabilities = [0.2, 0.1, 0.7]
    result = random.choices(values, weights=probabilities, k=1)[0]
    return result

def count_traps_around(grid, pos):
    num_traps = 0
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            neighbor = (pos[0] + dx, pos[1] + dy)
            if 0 <= neighbor[0] < len(grid) and 0 <= neighbor[1] < len(grid[neighbor[0]]):
                if grid[neighbor[0]][neighbor[1]] == "T":
                    num_traps += 1
    return num_traps

# Tra ve ma tran vuong ngau nhien va dap an
def generate_grid(n):
    # Khoi tao ma tran voi cac phan tu ngau nhien
    grid = [[random_element() for j in range(n)] for i in range(n)]
    
    # Gan trong so cho cac o trong
    answer_grid = copy.deepcopy(grid)
    for i in range(n):
        for j in range(n):
            if answer_grid[i][j] == "x":
                # Dem so luong T xung quanh vi tri (i, j)
                num_traps = count_traps_around(answer_grid, (i, j))
                # Gan so luong T xung quanh o trong
                answer_grid[i][j] = num_traps
    
    # Go tat ca gia tri T, G khoi ma tran
    question_grid = copy.deepcopy(answer_grid)
    for i in range(n):
        for j in range(n):
            if question_grid[i][j] in ["T", "G"]:
                question_grid[i][j] = "_"
                
    return question_grid, answer_grid
    
def main():
    # Nhap kich thuoc ma tran vuong
    n = int(input("Nhap kich thuoc ma tran vuong: "))
    
    # Nhap ten file luu ma tran
    fo = input("Nhap ten file luu ma tran: ")
    
    # Khoi tao ma tran vuong ngau nhien
    question_grid, answer_grid = generate_grid(n)
    # Tao lai ma tran vuong khac neu co trong so 0
    while 0 in [cell for row in question_grid for cell in row]:
        question_grid, answer_grid = generate_grid(n)
     
    # Ghi ma tran vao file
    with open(fo, "w") as f:
        for row in question_grid:
            f.write(", ".join(str(cell) for cell in row) + "\n")
            
    # # Ghi dap an ma tran vao file            
    # with open(f"demo_answer_{fo}", "w") as f:
    #     for row in answer_grid:
    #         f.write(", ".join(str(cell) for cell in row) + "\n")

    print(f"Ma tran da duoc luu vao file {fo}")

if __name__ == "__main__":
    main()