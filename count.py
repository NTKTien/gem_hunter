from main import *

# Dem so _ co trong ma tran
fi = "testcases/input_6.txt"
grid = read_input(fi)
count = 0
for i in range(len(grid)):
    for j in range(len(grid[0])):
        if grid[i][j] == "_":
            count += 1
print(f"Number of '_' in the grid: {count}")