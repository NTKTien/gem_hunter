import random

# Tra ve ngau nhien T, G hoac trong so
def random_element():
    return random.choice(["T", "G", "x"])

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

def main():
    # Nhap kich thuoc ma tran vuong
    n = int(input("Nhap kich thuoc ma tran vuong: "))
    
    # Nhap ten file luu ma tran
    fo = input("Nhap ten file luu ma tran: ")
    
    # Khoi tao ma tran voi cac phan tu ngau nhien
    grid = [[random_element() for j in range(n)] for i in range(n)]
    
    # Gan trong so cho cac o trong
    for i in range(n):
        for j in range(n):
            if grid[i][j] == "x":
                # Dem so luong T xung quanh vi tri (i, j)
                num_traps = count_traps_around(grid, (i, j))
                # Gan so luong T xung quanh o trong
                grid[i][j] = num_traps
    
    # Ghi dap an ma tran vao file            
    with open(f"answers_{fo}", "w") as f:
        for row in grid:
            f.write(", ".join(str(x) for x in row) + "\n")
    
    # Go tat ca gia tri T, G khoi ma tran
    for i in range(n):
        for j in range(n):
            if grid[i][j] in ["T", "G"]:
                grid[i][j] = "_"     
                
    # Ghi ma tran da duoc lam sach vao file
    with open(fo, "w") as f:
        for row in grid:
            f.write(", ".join(str(x) for x in row) + "\n")
       
    print(f"Ma tran da duoc luu vao file {fo}")

if __name__ == "__main__":
    main()