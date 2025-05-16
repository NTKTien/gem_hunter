from itertools import combinations
from pysat.solvers import Glucose3
import time
import copy
import sys
from multiprocessing import Process, Queue

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

# Ma hoa vi tri (i, j) thanh so thu tu neu mang duoc xem nhu mot mang 1 chieu
def encode_pos(pos, grid):
    return pos[0] * len(grid[0]) + pos[1] + 1 # tranh 0

# Phat sinh CNF
def generate_CNF(grid):
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

# Tra ve mang cac vi tri o trong
def find_empty_cells(grid):
    empty_cells = []
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == "_":
                empty_cells.append((i, j))
    return empty_cells

# Giai CNF bang Brute Force
def brute_force_solve(CNF_original):
    # Tao ban sao CNF
    CNF = copy.deepcopy(CNF_original)
    # Lap danh sach bien logic
    variables = set()
    for clause in CNF:
        for literal in clause:
            variables.add(abs(literal)) 
    variables = list(variables)
    num_variables = len(variables)
    # Kiem tra model
    def check_model(CNF, model):
        for clause in CNF:
            satisfied = False
            for literal in clause:
                if literal in model: # Mot bien logic thoa man, ca menh de thoa man (OR)
                    satisfied = True
                    break      
            if not satisfied:  # Mot menh de khong thoa man, ca CNF khong thoa man (AND)
                return False
        return True
    # Su dung day bits de tao tat ca cac hoan vi
    for bits in range(2 ** num_variables):
        model = [] 
        for k in range(num_variables):
             # 1 la T (+), 0 la G(-)
            if (bits >> k) & 1:
                model.append(variables[k])
            else:
                model.append(-variables[k])
        # Tra ve model hop le
        if check_model(CNF, model):
            return model
    return None

# Giai CNF bang backtracking
def backtracking_solve(CNF_original):
    # Tao ban sao CNF
    CNF = copy.deepcopy(CNF_original)
    # Lap danh sach bien logic
    variables = set()
    for clause in CNF:
        for literal in clause:
            variables.add(abs(literal))
    variables = list(variables)
    
    # Don gian hoa CNF khi mot gia tri duoc xac dinh
    def simplify_CNF(CNF, literal):
        new_CNF = []
        for clause in CNF:
            if literal in clause: # Luoc cac menh de da thoa man
                continue
            new_clause = [lit for lit in clause if lit != -literal]
            new_CNF.append(new_clause)
        return new_CNF
    
    def DPLL_solve(CNF, model):
        if not CNF: # Tra ve model khi tat ca menh de da duoc thoa man
            return model
        if any(len(clause) == 0 for clause in CNF): # Khong the thoa man CNF neu co menh de rong
            return None
        # LUOC MENH DE DON
        change = True
        while change:
            change = False
            unit_clauses = [clause[0] for clause in CNF if len(clause) == 1]
            if not unit_clauses: # Khong con menh de don
                break
            # Xu ly cac menh de don
            for unit in unit_clauses:
                if -unit in model: # Mau thuan
                    return None
                if unit in model: # Da xac dinh
                    continue
                model.append(unit) # Bat buoc mang gia tri tuong ung de thoa man
                CNF = simplify_CNF(CNF, unit) # Don gian hoa CNF
                change = True # Danh dau da thay doi
                # Kiem tra lai sau khi don gian hoa
                if not CNF:
                    return model
                if any(len(clause) == 0 for clause in CNF):
                    return None
        # TIM CAC BIEN LOGIC CHI XUAT HIEN MOT DANG
        all_literals = [literal for clause in CNF for literal in clause]
        pure_literals = []
        for var in variables:
            if var not in model and -var not in model: # Chua xac dinh
                pos_appears = var in all_literals
                neg_appears = -var in all_literals
                if pos_appears != neg_appears: # Chi xuat hien mot dang
                    pure_literals.append(var if pos_appears else -var)
        # Gan gia tri cho cac bien logic chi xuat hien mot dang
        if pure_literals:
            for pure in pure_literals:
                model.append(pure)
                CNF = simplify_CNF(CNF, pure)
            # Kiem tra lai sau khi don gian hoa
            if not CNF:
                return model
        # DE QUY CHON BIEN LOGIC
        # Neu CNF van con, chon bien de phan nhanh
        if CNF:
            # Dem so lan xuat hien cua cac bien logic chua xac dinh
            var_counts = {}
            for clause in CNF:
                for literal in clause:
                    var = abs(literal)
                    if var not in model and -var not in model:
                        var_counts[var] = var_counts.get(var, 0) + 1
            if not var_counts: # Tat ca bien da duoc xac dinh
                return model
            # Chon bien xuat hien nhieu nhat
            next_var = max(var_counts.items(), key=lambda x: x[1])[0]
            # Thu voi dang +
            model_pos = model.copy()
            model_pos.append(next_var)
            new_model = DPLL_solve(simplify_CNF(CNF, next_var), model_pos)
            if new_model is not None:
                return new_model
            
            # Thu voi dang -
            model_neg = model.copy()
            model_neg.append(-next_var)
            return DPLL_solve(simplify_CNF(CNF, -next_var), model_neg)
        # CAC MENH DE DA THOA MAN
        return model 
        
    # Chay thuat toan DPLL
    return DPLL_solve(CNF, [])

def backtracking_solve_fixed(CNF_original):
    # Tao ban sao CNF
    CNF = copy.deepcopy(CNF_original)
    # Lap danh sach bien logic
    variables = set()
    for clause in CNF:
        for literal in clause:
            variables.add(abs(literal))
    variables = list(variables)
    
    # Don gian hoa CNF khi mot gia tri duoc xac dinh
    def simplify_CNF(CNF, literal):
        new_CNF = []
        for clause in CNF:
            if literal in clause:  # Luoc cac menh de da thoa man
                continue
            new_clause = [lit for lit in clause if lit != -literal]
            new_CNF.append(new_clause)
        return new_CNF
    
    def DPLL_solve(CNF, model):
        # Tra ve model khi tat ca menh de da duoc thoa man
        if not CNF:
            return model
            
        # Khong the thoa man CNF neu co menh de rong
        if any(len(clause) == 0 for clause in CNF):
            return None
        
        # ---- CẢI TIẾN 1: UNIT PROPAGATION HIỆU QUẢ HƠN ----
        # Xử lý các unit clauses cho đến khi không còn
        change = True
        while change:
            change = False
            unit_clauses = [clause[0] for clause in CNF if len(clause) == 1]
            if not unit_clauses:
                break
                
            for unit in unit_clauses:
                if -unit in model:
                    return None  # Mâu thuẫn phát hiện
                if unit in model:
                    continue
                    
                model.append(unit)
                CNF = simplify_CNF(CNF, unit)
                change = True
                
                # Kiểm tra lại sau khi đơn giản hóa
                if not CNF:
                    return model
                if any(len(clause) == 0 for clause in CNF):
                    return None
        
        # ---- CẢI TIẾN 2: PURE LITERAL ELIMINATION HIỆU QUẢ HƠN ----
        # Tìm pure literals (chỉ xuất hiện dạng dương hoặc dạng âm)
        all_literals = [lit for clause in CNF for lit in clause]
        pure_literals = []
        
        for var in variables:
            if var not in model and -var not in model:  # Chưa xác định
                pos_appears = var in all_literals
                neg_appears = -var in all_literals
                
                if pos_appears and not neg_appears:  # Chỉ xuất hiện dạng dương
                    pure_literals.append(var)
                elif neg_appears and not pos_appears:  # Chỉ xuất hiện dạng âm
                    pure_literals.append(-var)
        
        # Áp dụng pure literals
        if pure_literals:
            for pure in pure_literals:
                model.append(pure)
                CNF = simplify_CNF(CNF, pure)
            
            # Kiểm tra lại sau khi đơn giản hóa
            if not CNF:
                return model
        
        # ---- CẢI TIẾN 3: CHỌN BIẾN THEO HEURISTIC ----
        # Nếu CNF vẫn còn, chọn biến để phân nhánh
        if CNF:
            # Heuristic: Chọn biến xuất hiện nhiều nhất trong CNF
            var_counts = {}
            for clause in CNF:
                for lit in clause:
                    var = abs(lit)
                    if var not in model and -var not in model:  # Chưa xác định
                        var_counts[var] = var_counts.get(var, 0) + 1
            
            if not var_counts:  # Mọi biến đã được xác định
                return model
                
            # Chọn biến xuất hiện nhiều nhất
            next_var = max(var_counts.items(), key=lambda x: x[1])[0]
            
            # Thử với dạng +
            model_pos = model.copy()
            model_pos.append(next_var)
            result = DPLL_solve(simplify_CNF(CNF, next_var), model_pos)
            if result:
                return result
                
            # Thử với dạng -
            model_neg = model.copy()
            model_neg.append(-next_var)
            return DPLL_solve(simplify_CNF(CNF, -next_var), model_neg)
        
        return model  # Tất cả mệnh đề đã được thỏa mãn
    
    # Chay thuat toan DPLL
    return DPLL_solve(CNF, [])

# Giai CNF theo thuat toan da chon va tra ket qua vao hang doi
def solve_CNF(grid, algorithm, result_queue):
    CNF = generate_CNF(grid)
    model = []
    solution = copy.deepcopy(grid)
    start_time = 0
    end_time = 0
    # Chay thuat toan
    if algorithm == "pySAT":
        start_time = time.time()
        solver = Glucose3()
        for clause in CNF:
            solver.add_clause(clause)
        # Gan gia tri neu tim duoc solution
        if solver.solve():
            model = solver.get_model()
        end_time = time.time()    
    elif algorithm == "Brute Force":
        start_time = time.time()
        model = brute_force_solve(CNF)
        end_time = time.time()
    elif algorithm == "Backtracking":
        start_time = time.time()
        model = backtracking_solve(CNF)
        end_time = time.time()
    else:
        raise ValueError("Invalid algorithm. Choose 'pySAT', 'Brute Force' or 'Backtracking'.")
    # Chuyen model thanh ma tran
    if model:
        for i in range(len(solution)):
            for j in range(len(solution[i])):
                if solution[i][j] == "_":
                    e = encode_pos((i, j), solution)
                    if e in model:
                        solution[i][j] = "T"
                    else:
                        solution[i][j] = "G"
        print(f"{algorithm} solution found")
    else:
        print(f"No solution found with {algorithm}")
        solution = None
    print(f"Execution time: {(end_time - start_time):.10f}s")
    result_queue.put({"solution": solution, "time": end_time - start_time})

def main(timeout = 60):
    fi = "input_3.txt" # file input
    fo = "output_3.txt" # file output
    grid = read_input(fi)
    results = dict()
    q = Queue()
    print("\n")
    # ---------------- PY-SAT ----------------
    print("Running pySAT...")
    p1 = Process(target=solve_CNF, args=(grid, "pySAT", q))
    p1.start()
    p1.join(timeout=timeout)
    if p1.is_alive():
        p1.terminate()
        print(f"TIMEOUT!\n")
        results["pySAT"] = "TIMEOUT"
    else:
        print("Run successfully\n")
        results["pySAT"] = q.get()
    
    # ---------------- BRUTE FORCE ----------------
    print("Running Brute Force...")
    p2 = Process(target=solve_CNF, args=(grid, "Brute Force", q))
    p2.start()
    p2.join(timeout=timeout)
    if p2.is_alive():
        p2.terminate()
        print(f"TIMEOUT!\n")
        results["Brute Force"] = "TIMEOUT"
    else:
        print("Run successfully\n")
        results["Brute Force"] = q.get()
    
    # ---------------- BACKTRACKING ----------------
    print("Running Backtracking...")
    p3 = Process(target=solve_CNF, args=(grid, "Backtracking", q))
    p3.start()
    p3.join(timeout=timeout)
    if p3.is_alive():
        p3.terminate()
        print(f"TIMEOUT!\n")
        results["Backtracking"] = "TIMEOUT"
    else:
        print("Run successfully\n")
        results["Backtracking"] = q.get()
        
    # ---------------- GHI RA FILE ----------------
    with open(fo, "w") as f:
        for algorithm in results:
            f.write(f"----- {algorithm} -----\n")
            if results[algorithm] == "TIMEOUT":
                f.write("TIMEOUT\n")
            else:
                solution = results[algorithm]["solution"]
                if solution:
                    for row in solution:
                        f.write(", ".join(map(str, row)) + "\n")
                else:
                    f.write("No solution found\n")
                f.write(f"Execution time: {results[algorithm]['time']:.10f}s\n")
            f.write("\n")
            
    print(f"Results written to {fo}.")

if __name__ == "__main__":
    main(timeout = 60)