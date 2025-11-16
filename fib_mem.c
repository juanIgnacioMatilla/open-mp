#include <stdio.h>
#include <stdlib.h>
#include <time.h>

long long memo[200];   // Soporta hasta n=199, más que suficiente para el TP

long long fib_mem(int n) {
    if (n < 2)
        return n;

    if (memo[n] != -1)
        return memo[n];

    memo[n] = fib_mem(n-1) + fib_mem(n-2);
    return memo[n];
}

int main(int argc, char **argv) {
    int n = atoi(argv[1]);

    // Inicializamos el arreglo de memo en -1
    for (int i = 0; i < 200; i++)
        memo[i] = -1;

    // Medición de tiempo con clock() (sin OpenMP)
    clock_t start = clock();

    long long result = fib_mem(n);

    clock_t end = clock();
    double time_taken = (double)(end - start) / CLOCKS_PER_SEC;

    printf("Resultado memoization = %lld\n", result);
    printf("Tiempo = %f segundos\n", time_taken);

    return 0;
}

