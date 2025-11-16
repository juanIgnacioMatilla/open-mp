import subprocess
import time
import statistics
import matplotlib.pyplot as plt

# ======================
# CONFIGURACIÓN
# ======================
NS = [8, 9, 10, 11, 12, 13, 14]   # valores de N a testear
THREADS = [1, 2, 4, 8]            # hilos para la versión paralela
REPS = 3                          # repeticiones por punto

seq_exec = "./queens_seq"
par_exec = "./queens_par"

def medir_tiempo(cmd):
    """Ejecuta cmd y devuelve el tiempo en segundos."""
    t0 = time.time()
    _ = subprocess.check_output(cmd, shell=True).decode()
    return time.time() - t0

# ======================
# SECUENCIAL
# ======================
print("\n=== Ejecutando versión SECUENCIAL ===\n")

times_seq_mean = []
times_seq_std  = []

for N in NS:
    print(f"Secuencial N={N}...")
    mediciones = [medir_tiempo(f"{seq_exec} {N}") for _ in range(REPS)]
    times_seq_mean.append(statistics.mean(mediciones))
    times_seq_std.append(statistics.stdev(mediciones))

# ======================
# PARALELO
# ======================
print("\n=== Ejecutando versión PARALELA ===\n")

times_par_mean = {th: [] for th in THREADS}
times_par_std  = {th: [] for th in THREADS}

for th in THREADS:
    print(f"\n--- Hilos = {th} ---")
    for N in NS:
        print(f"Paralelo N={N} (threads={th})...")
        mediciones = [
            medir_tiempo(f"OMP_NUM_THREADS={th} {par_exec} {N}")
            for _ in range(REPS)
        ]
        times_par_mean[th].append(statistics.mean(mediciones))
        times_par_std[th].append(statistics.stdev(mediciones))

# ======================
# GRAFICAR
# ======================
plt.figure(figsize=(11,6))

# curva secuencial
plt.errorbar(NS, times_seq_mean, yerr=times_seq_std, fmt="-o",
             capsize=4, label="Secuencial")

# curvas paralelas
for th in THREADS:
    plt.errorbar(NS, times_par_mean[th], yerr=times_par_std[th],
                 fmt="-o", capsize=4,
                 label=f"Paralelo {th} hilos")

plt.xlabel("Tamaño del tablero N")
plt.ylabel("Tiempo (segundos)")
plt.title("Tiempo de ejecución — N Queens (secuencial vs OpenMP)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("queens_benchmark.png", dpi=150)
plt.show()

print("\nBenchmark finalizado. Gráfico guardado como queens_benchmark.png\n")

