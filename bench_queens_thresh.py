#!/usr/bin/env python3
import subprocess
import time
import statistics
import matplotlib.pyplot as plt
import os

# ======================
# CONFIGURACIÓN
# ======================
EXEC_SEQ = "./queens_seq"          # versión secuencial
EXEC_PAR = "./queens_thr"   # versión paralela con thresholding

NS = [10, 11, 12, 13, 14, 15]    # tamaños de tablero
TH_LIST = [1, 2, 3, 4]             # thresholds a promediar
RUNS = 3                           # cantidad de repeticiones por caso
TIMEOUT = 60.0                     # segundos máximo por ejecución
NUM_THREADS = 8                    # hilos para la versión paralela

# ======================
# HELPERS
# ======================

def run_timed(cmd_list, timeout=TIMEOUT, env=None):
    """
    Ejecuta un comando (lista) midiendo wall-clock time.
    Devuelve tiempo en segundos o None si hay error/timeout.
    """
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            env=env
        )
    except subprocess.TimeoutExpired:
        print("   -> TIMEOUT")
        return None
    t1 = time.time()

    if proc.returncode != 0:
        print("   -> ERROR (returncode != 0)")
        print(proc.stderr)
        return None

    return t1 - t0

# ======================
# MEDICIÓN SECUENCIAL
# ======================

print("\n=== Midiendo versión SECUENCIAL ===\n")

times_seq_mean = []
times_seq_std  = []

for N in NS:
    samples = []
    print(f"N = {N} (sec): ", end="", flush=True)
    for r in range(RUNS):
        t = run_timed([EXEC_SEQ, str(N)])
        if t is not None:
            samples.append(t)
            print(f"{t:.3f}s ", end="", flush=True)
    print()

    if samples:
        times_seq_mean.append(statistics.mean(samples))
        times_seq_std.append(
            statistics.pstdev(samples) if len(samples) > 1 else 0.0
        )
    else:
        # si no hubo muestras válidas, ponemos NaN para que Matplotlib lo saltee
        times_seq_mean.append(float("nan"))
        times_seq_std.append(0.0)

# ======================
# MEDICIÓN PARalela (agrupada sobre TH)
# ======================

print("\n=== Midiendo versión PARALELA con thresholding (agrupada sobre TH) ===\n")

times_par_mean = []
times_par_std  = []

# preparamos env con OMP_NUM_THREADS fijo
base_env = os.environ.copy()
base_env["OMP_NUM_THREADS"] = str(NUM_THREADS)

for N in NS:
    all_samples_for_N = []
    print(f"N = {N} (par, TH in {TH_LIST}):")
    for TH in TH_LIST:
        print(f"  TH = {TH}: ", end="", flush=True)
        for r in range(RUNS):
            t = run_timed([EXEC_PAR, str(N), str(TH)], env=base_env)
            if t is not None:
                all_samples_for_N.append(t)
                print(f"{t:.3f}s ", end="", flush=True)
        print()
    if all_samples_for_N:
        times_par_mean.append(statistics.mean(all_samples_for_N))
        times_par_std.append(
            statistics.pstdev(all_samples_for_N) if len(all_samples_for_N) > 1 else 0.0
        )
    else:
        times_par_mean.append(float("nan"))
        times_par_std.append(0.0)

# ======================
# GRAFICAR
# ======================

plt.figure(figsize=(10, 6))

# Secuencial
plt.errorbar(
    NS, times_seq_mean, yerr=times_seq_std,
    fmt="-o", capsize=4, label="Secuencial"
)

# Paralelo (promedio sobre todos los TH)
plt.errorbar(
    NS, times_par_mean, yerr=times_par_std,
    fmt="-o", capsize=4, label="Paralelo TH (media sobre TH)"
)

plt.xlabel("Tamaño N del tablero")
plt.ylabel("Tiempo (s)")
plt.title("Benchmark N-Reinas — Secuencial vs Paralelo con Thresholding (agrupado)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("queens_thresh_benchmark.png", dpi=150)
plt.show()

print("\nBenchmark finalizado. Gráfico guardado como queens_thresh_benchmark.png\n")

