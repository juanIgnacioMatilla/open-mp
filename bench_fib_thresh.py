#!/usr/bin/env python3
import subprocess
import statistics
import matplotlib.pyplot as plt

EXEC = "./fib_thresh"

# Lista de thresholds a probar
TH_LIST = [5, 10, 15, 20, 25, 30]

# Ns razonables por cada TH
N_GRID = {
    5:  [30, 32, 34, 35],
    10: [30, 32, 34, 35, 38, 40, 42],
    15: [30, 32, 34, 35, 38, 40, 42, 45],
    20: [30, 32, 34, 35, 38, 40, 42, 45, 48, 50],
    25: [30, 32, 34, 35, 38, 40, 42, 45, 48, 50, 53, 55],
    30: [30, 32, 34, 35, 38, 40, 42, 45, 48, 50, 53, 55, 58],
}

TIMEOUT = 8.0  # segundos
RUNS = 3       # cantidad de mediciones por punto

results = {}

print("Ejecutando benchmarks...\n")

for th in TH_LIST:
    Ns_ok = []
    means = []
    stds = []

    print(f"== TH = {th} ==")
    for n in N_GRID[th]:
        print(f"  N={n} ... ", end="", flush=True)

        samples = []

        for r in range(RUNS):
            try:
                proc = subprocess.run(
                    [EXEC, str(n), str(th)],
                    text=True,
                    capture_output=True,
                    timeout=TIMEOUT,
                )
            except subprocess.TimeoutExpired:
                print("TIMEOUT")
                samples = None
                break

            if proc.returncode != 0:
                print("ERROR (returncode != 0)")
                print(proc.stdout)
                print(proc.stderr)
                samples = None
                break

            # Buscar la línea con "Tiempo = X"
            t_exec = None
            for line in proc.stdout.splitlines():
                if "Tiempo =" in line:
                    t_exec = float(line.split("=")[1].strip().split()[0])
                    break

            if t_exec is None:
                print("ERROR al parsear tiempo")
                print(proc.stdout)
                samples = None
                break

            samples.append(t_exec)

        if samples is None:
            break

        mean_t = statistics.mean(samples)
        std_t = statistics.stdev(samples) if len(samples) > 1 else 0.0

        Ns_ok.append(n)
        means.append(mean_t)
        stds.append(std_t)

        print(f"{mean_t:.3f}s (std={std_t:.3f})")

    results[th] = (Ns_ok, means, stds)
    print()

# ================== GRAFICAR ==================

plt.figure(figsize=(10,5))

for th, (Ns_ok, means, stds) in results.items():
    if not Ns_ok:
        continue

    # Curva con barras de error
    plt.errorbar(Ns_ok, means, yerr=stds, marker="o", capsize=4, label=f"TH={th}")

    # Marcar el último punto
    last_n = Ns_ok[-1]
    last_t = means[-1]
    plt.scatter([last_n], [last_t], marker="s", s=80)
    plt.text(last_n, last_t, f"  N={last_n}", fontsize=8)

plt.xlabel("N")
plt.ylabel("Tiempo (s)")
plt.title("Tiempo de ejecución de fib_thresh (3 runs, promedio ± std)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

