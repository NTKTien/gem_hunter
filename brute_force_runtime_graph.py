import matplotlib.pyplot as plt

k_values = [4, 10, 15, 18, 24]
times = [0.00049, 0.00506, 0.10618, 0.89278, 52.08326]

plt.plot(k_values, times, marker='o', color='red')
plt.xlabel('Number of empty cells (k)')
plt.ylabel('Running time (seconds)')
plt.title('The dependency of Running time on the Number of empty cells with Brute Force')
plt.grid(True)
plt.yscale('log')
plt.show()
