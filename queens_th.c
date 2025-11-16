#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <omp.h>

int N;
int TH;                  // profundidad hasta la cual se paraleliza
long long solutions = 0;

bool is_safe(int *board, int row, int col) {
    for (int i = 0; i < row; i++) {
        if (board[i] == col ||
            board[i] - i == col - row ||
            board[i] + i == col + row)
            return false;
    }
    return true;
}

// ---- versión híbrida: paralelo sólo hasta TH ---- //
void solve_thr(int row, int *board) {

    // Caso base
    if (row == N) {
        #pragma omp atomic
        solutions++;
        return;
    }

    for (int col = 0; col < N; col++) {
        if (is_safe(board, row, col)) {

            // copiar tablero para la siguiente rama
            int *new_board = malloc(N * sizeof(int));
            for (int k = 0; k < row; k++) new_board[k] = board[k];
            new_board[row] = col;

            if (row < TH) {
                // paralelizamos solo las primeras TH filas
                #pragma omp task firstprivate(new_board, row)
                {
                    solve_thr(row + 1, new_board);
                    free(new_board);
                }
            } else {
                // parte secuencial optimizada
                solve_thr(row + 1, new_board);
                free(new_board);
            }
        }
    }

    #pragma omp taskwait
}

int main(int argc, char **argv) {

    if (argc < 3) {
        printf("Uso: %s N TH\n", argv[0]);
        return 1;
    }

    N  = atoi(argv[1]);
    TH = atoi(argv[2]);
    solutions = 0;

    double t0 = omp_get_wtime();

    #pragma omp parallel
    {
        #pragma omp single
        {
            int *board = calloc(N, sizeof(int));
            solve_thr(0, board);
            free(board);
        }
    }

    double t1 = omp_get_wtime();

    printf("Soluciones = %lld\n", solutions);
    printf("Threshold = %d\n", TH);
    printf("Tiempo = %f segundos\n", t1 - t0);

    return 0;
}

