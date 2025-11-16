#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <omp.h>

int N;                      
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

void solve(int row, int *board) {
    if (row == N) {
        #pragma omp atomic
        solutions++;
        return;
    }

    for (int col = 0; col < N; col++) {
        if (is_safe(board, row, col)) {

            // Copiamos el tablero para la rama nueva
            int *new_board = malloc(N * sizeof(int));
            for (int k = 0; k < row; k++)
                new_board[k] = board[k];
            new_board[row] = col;

            // CADA expansión del árbol es una task
            #pragma omp task firstprivate(new_board, row)
            {
                solve(row + 1, new_board);
                free(new_board);
            }
        }
    }

    // Asegura que todas las tareas hijas finalicen
    #pragma omp taskwait
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("Uso: %s N\n", argv[0]);
        return 1;
    }

    N = atoi(argv[1]);
    solutions = 0;

    #pragma omp parallel
    {
        #pragma omp single
        {
            int *board = malloc(N * sizeof(int));
            solve(0, board);
            free(board);
        }
    }

    printf("Soluciones para %d reinas: %lld\n", N, solutions);
    return 0;
}

