import matplotlib.pyplot as plt

k_values = [8, 12, 18]
times = [0.0003049374, 0.0025827885, 0.6744847298]

plt.plot(k_values, times, marker='o', color='red')
plt.xlabel('Number of empty cells')
plt.ylabel('Running time (seconds)')
plt.title('Running time & Number of empty cells with Brute Force')
plt.grid(True)
plt.yscale('log')
plt.show()
