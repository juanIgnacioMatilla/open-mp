#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Fibonacci iterativo (O(n))
long long fib_iter(int n) {
    if (n < 2) return n;

    long long a = 0, b = 1, tmp;
    for (int i = 2; i <= n; i++) {
        tmp = a + b;
        a = b;
        b = tmp;
    }
    return b;
}

// time en segundos
double now() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        printf("Uso: %s <n>\n", argv[0]);
        return 1;
    }

    int n = atoi(argv[1]);

    double t1 = now();
    long long result = fib_iter(n);
    double t2 = now();

    printf("Resultado iterativo = %lld\n", result);
    printf("Tiempo = %f segundos\n", t2 - t1);

    return 0;
}

