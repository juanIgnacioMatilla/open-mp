#!/usr/bin/env python3
import subprocess
import statistics
import matplotlib.pyplot as plt

# ======================
# CONFIGURACIÓN
# ======================
EXEC_PAR = "./queens_thr"      # versión paralela con thresholding

NS = [10, 11, 12, 13, 14, 15]   # tamaños del tablero
TH_LIST = [1, 3, 7, 8, 9, 10]       # thresholds a comparar

RUNS = 3                        # repeticiones por punto
TIMEOUT = 60.0                  # timeout por ejecución
NUM_THREADS = 8                 # cantidad de hilos OpenMP

def run_once(N, TH):
    """Ejecuta una corrida del programa y devuelve el tiempo en segundos."""
    try:
        cmd = f"OMP_NUM_THREADS={NUM_THREADS} {EXEC_PAR} {N} {TH}"
        proc = subprocess.run(cmd, shell=True, capture_output=True,
                              text=True, timeout=TIMEOUT)

        if proc.returncode != 0:
            return None

        # buscar "Tiempo = X"
        for line in proc.stdout.splitlines():
            if "Tiempo =" in line:
                token = line.split("=")[1].strip().split()[0]
                return float(token)

    except subprocess.TimeoutExpired:
        return None

    return None


# ======================
# MEDIR
# ======================
print("\n== Benchmark sólo TH (paralelo) ==\n")

results_mean = {TH: [] for TH in TH_LIST}
results_std  = {TH: [] for TH in TH_LIST}

for TH in TH_LIST:
    print(f"\n--- TH={TH} ---")
    for N in NS:
        print(f"N={N}... ", end="", flush=True)
        runs = []

        for r in range(RUNS):
            t = run_once(N, TH)
            runs.append(t)

        # Filtrar errores/timeouts
        runs = [x for x in runs if x is not None]

        if len(runs) == 0:
            print("TIMEOUT / ERROR")
            results_mean[TH].append(None)
            results_std[TH].append(None)
        else:
            m = statistics.mean(runs)
            sd = statistics.stdev(runs) if len(runs) > 1 else 0.0
            results_mean[TH].append(m)
            results_std[TH].append(sd)

            print(f"{m:.3f} s  (std={sd:.3f})")


# ======================
# GRAFICAR
# ======================
plt.figure(figsize=(10,6))

for TH in TH_LIST:
    means = results_mean[TH]
    stds  = results_std[TH]

    # Filtrar Ns válidos
    Ns_ok = [NS[i] for i in range(len(NS)) if means[i] is not None]
    m_ok  = [means[i] for i in range(len(NS)) if means[i] is not None]
    sd_ok = [stds[i]  for i in range(len(NS)) if means[i] is not None]

    if len(Ns_ok) == 0:
        continue

    plt.errorbar(Ns_ok, m_ok, yerr=sd_ok, marker="o", capsize=4,
                 label=f"TH={TH}")

plt.xlabel("Tamaño N del tablero")
plt.ylabel("Tiempo (s)")
plt.title("Benchmark N-Reinas — Comparación entre distintos Threshold (TH)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

