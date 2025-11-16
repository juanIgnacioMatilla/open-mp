#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

long long TH = 20;   // threshold

long long fib_thr(long long n) {
    if (n < 2) return n;

    // Si n es menor al umbral, resolver secuencialmente
    if (n <= TH) {
        long long a = 0, b = 1, tmp;
        for (long long i = 2; i <= n; i++) {
            tmp = a + b;
            a = b;
            b = tmp;
        }
        return b;
    }

    long long x, y;

    #pragma omp task shared(x)
    x = fib_thr(n - 1);

    #pragma omp task shared(y)
    y = fib_thr(n - 2);

    #pragma omp taskwait
    return x + y;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("Uso: %s <N> <threshold>\n", argv[0]);
        return 1;
    }

    long long n  = atoll(argv[1]);
    TH = atoll(argv[2]);

    long long result;

    double t0 = omp_get_wtime();
    #pragma omp parallel
    {
        #pragma omp single
        result = fib_thr(n);
    }
    double t1 = omp_get_wtime();

    printf("Resultado thresholding = %lld\n", result);
    printf("Threshold = %lld\n", TH);
    printf("Tiempo = %f segundos\n", t1 - t0);

    return 0;
}

