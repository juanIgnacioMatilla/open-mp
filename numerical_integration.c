#include <stdio.h>
#include <omp.h>

static long num_steps = 100000000;
double step;

void main() {
    int i;
    double x, pi, sum = 0.0;

    step = 1.0 / (double) num_steps;

    #pragma omp parallel private(i, x)
    {
        int tid = omp_get_thread_num();
        double t_start = omp_get_wtime();
        double local_sum = 0.0;

        #pragma omp for
        for (i = 0; i < num_steps; i++) {
            x = (i + 0.5) * step;
            local_sum += 4.0 / (1.0 + x * x);
        }

        // Combine results
        #pragma omp atomic
        sum += local_sum;

        double t_end = omp_get_wtime();

        printf("Thread %d time: %f seconds\n",
               tid, t_end - t_start);
    }

    pi = step * sum;

    printf("PI = %.15f\n", pi);
}

