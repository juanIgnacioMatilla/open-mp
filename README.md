## a) Fibonacci paralelizado

_Dado el siguiente código ya paralelizado con OpenMP, que corresponde al conocido problema de Fibonacci en su versión recursiva:_
```c
#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
int fib(int n) {
  int i, j;
  if (n<2)
     return n;
  else {
     #pragma omp task shared(i)
     i=fib(n-1);
     #pragma omp task shared(j)
     j=fib(n-2);
     #pragma omp taskwait
     return i+j;
  }
}
int main(int argc, char **argv){
  int n, result;
  char *a = argv[1];
  n = atoi(a);
  #pragma omp parallel
  {
     #pragma omp single
     result = fib(n);
  }
  printf("Result is %d\n", result);
}
```
_Poné a funcionar en tu computadora el código, previo a instalar OpenMP (ver videos en el material del curso).
Este código utiliza las construcciones task y taskwait, que no vimos en las slides. A no desesperar! La idea es que investigues cómo funcionan acá: https://hpc2n.github.io/Task-based-parallelism/branch/master/task-basics-1/#
Luego, respondé a las siguientes preguntas:
¿Por qué crees que se ha utilizado cada #pragma en esos lugares específicos? Explicá qué sentido tiene esta combinación para paralelizar el programa._


El `#pragma omp parallel` crea el equipo de threads que ejecutará todas las tareas. Dentro de él se usa `#pragma omp single` para asegurar que solo un thread realice la llamada inicial a `fib(n);` de lo contrario todos los threads ejecutarían la misma llamada redundante.
En la función fib, cada llamada recursiva independiente (`fib(n-1)` y `fib(n-2)`) se marca con `#pragma omp task` para que el runtime pueda ejecutarlas en paralelo en cualquier thread disponible.
Luego se utiliza `#pragma omp taskwait` antes de devolver i + j para sincronizar las dos tareas y garantizar que ambas hayan finalizado, dado que sus resultados son necesarios para continuar. Mas en detalle cada linea `#pragma`:

```c
#pragma omp parallel
```

Crea un único equipo de threads al inicio del programa.
Es necesario para que las tareas generadas durante la recursión puedan ejecutarse en paralelo sin crear nuevos threads en cada llamada a fib().

```c
#pragma omp single
```

Garantiza que solo un thread realice la llamada inicial a fib(n).
Evita que todos los threads ejecuten la misma llamada recursiva y dupliquen el trabajo.
Los demás threads quedan libres para ejecutar las tareas que se generen después.

```c
#pragma omp task shared(i)
```

Crea una tarea para la rama recursiva fib(n-1).
Esta tarea podrá ser tomada y ejecutada por cualquier thread disponible del equipo, permitiendo paralelizar una de las dos ramas del árbol de Fibonacci.

```c
#pragma omp task shared(j)
```

Crea una segunda tarea independiente para la rama fib(n-2).
Esta segunda rama también puede ejecutarse en paralelo con la anterior, aprovechando la independencia entre ambas llamadas recursivas.

```c
#pragma omp taskwait
```

Obliga al thread actual a esperar a que las dos tareas anteriores (las llamadas recursivas) terminen.
Es necesario porque los valores i y j deben estar computados antes de poder retornar i + j.
Sin esta espera, se produciría una condición de carrera y el resultado podría ser incorrecto.



## b) Comparacion de tiempos contra Fibonacci secuencial 
_Utiliza el comando de consola "time", para comprobar si el tiempo del programa completo se reduce al pasar de la versión 
compilada secuencial (desactivando OpenMP al compilar) a la que utiliza OpenMP con varios hilos. Podés también utilizar omp_get_wtime() 
para medir por separado el tiempo total y el de la parte paralela. Parametrizar el programa con un valor por encima de 45 debiera
llevar a tiempos razonablemente altos para probar. ¿Qué sucede y por qué?_

Para evaluar el rendimiento del programa Fibonacci con y sin OpenMP, se generaron dos ejecutables distintos: uno versión secuencial y otro con paralelismo por tareas.


Versión paralela (OpenMP):

```bash
gcc -O2 -fopenmp fib.c -o fib_omp
```

Versión secuencial (sin OpenMP):

```bash
gcc -O2 fib.c -o fib_seq
```


Esto permite comparar el rendimiento real del algoritmo recursivo de Fibonacci bajo ambos modelos.


Ejecución con time usando N = 15
- Versión secuencial:
```bash
time ./fib_seq 15
Result is 610


real    0m0.003s
user    0m0.002s
sys     0m0.001s
```

- Versión paralela (OpenMP con tasks):
```bash
time ./fib_omp 15
Result is 610


real    0m0.030s
user    0m0.270s
sys     0m0.010s
```

Interpretación: El tiempo secuencial es mucho menor (≈0.003 s) a la versión paralela tarda diez veces más (≈0.030 s). El consumo de CPU (user) es especialmente revelador:
-   Secuencial: 0.002 s
-   Paralela: 0.270 s
  Esto indica que los threads de OpenMP estuvieron trabajando mucho más tiempo administrando tareas que calculando Fibonacci.


Ejecución con time usando N = 30
- Versión secuencial
```c
time ./fib_seq 30
Result is 832040

real    0m0.004s
user    0m0.001s
sys     0m0.001s
```

- Versión paralela (OpenMP con tasks)
```bash
time ./fib_omp 30
Result is 832040


real    0m2.574s
user    0m32.325s
sys     0m0.474s
```

Interpretación: La versión secuencial sigue siendo mucho mas rápida (≈0.004 s) que la versión paralela (≈2.574 s). El tiempo de CPU utilizado (user = 32.3 s) muestra claramente que los hilos consumen decenas de segundos gestionando tasks, pero el trabajo útil es mínimo. Este comportamiento es el opuesto al esperado en un paralelismo bien aprovechado.


**Conclusión general**


El uso de `#pragma omp task` para paralelizar Fibonacci recursivo no solo no acelera el programa, sino que lo vuelve muchísimo más lento. Esto ocurre porque Fibonacci recursivo genera un número exponencial de llamadas y cada una crea una task muy pequeña. El costo de crear, programar, sincronizar y destruir estas tareas (task + taskwait) es mucho mayor que el trabajo real que realiza cada tarea.


Esto genera que el overhead del runtime de OpenMP represente el mayor tiempo de ejecución. Como consecuencia, el tiempo total aumenta drásticamente en la versión paralela.

## c) Optimizaciones Fibonacci 

_Implementar las posibles optimizaciones clásicas para problemas recursivos en caso que apliquen 
(transformación a código iterativo, memoization, thresholding). Luego, siguiendo la lógica de c), 
reimplementá lo necesario y probá el efecto de las optimizaciones midiendo nuevamente los tiempos. ¿Qué cambios hay?_

**Versión iterativa `fib_iter.c`**

Se probó la versión iterativa secuencial del algoritmo de Fibonacci para distintos valores de entrada:
```bash
$ ./fib_iter 30
Resultado iterativo = 832040
Tiempo = 0.000001 segundos
```
```bash
$ ./fib_iter 90
Resultado iterativo = 2880067194370816120
Tiempo = 0.000002 segundos
```
```bash
$ ./fib_iter 120
Resultado iterativo = 4376692037216111008
Tiempo = 0.000002 segundos
```

Análisis de tiempos

Los tiempos son extremadamente bajos (del orden de 1–2 microsegundos) incluso para valores muy grandes como 90 y 120.
Esto ocurre porque:
- La versión iterativa tiene complejidad O(n).
- Cada iteración realiza solo una suma y dos asignaciones.
- Para n = 120, el algoritmo ejecuta únicamente 120 iteraciones, lo cual es insignificante para un CPU moderno.


En contraste, el algoritmo recursivo original tiene complejidad exponencial O(2ⁿ), lo cual explica los tiempos enormes para n moderados.


Implementar OpenMP en un algoritmo iterativo de este tipo no tiene sentido porque no existe paralelismo natural en esta versión del algoritmo ya que cada número depende del anterior:

`F(n) = F(n-1) + F(n-2)`

Esto genera una dependencia de datos estricta entre iteraciones que por lo tanto no permite paralelizar el bucle.




**Versión con Memoization `fib_mem.c`**

Se probó la versión recursiva con memoization del algoritmo de Fibonacci (sin OpenMP), donde se almacena cada resultado calculado para evitar recomputarlo múltiples veces.

```bash
$ ./fib_mem 30
Resultado memoization = 832040
Tiempo = 0.000002 segundos
```
```bash
$ ./fib_mem 90
Resultado memoization = 2880067194370816120
Tiempo = 0.000002 segundos
```
```bash
$ ./fib_mem 120
Resultado memoization = 4376692037216111008
Tiempo = 0.000003 segundos
```

Análisis de tiempos


Los tiempos obtenidos son casi idénticos a los de la versión iterativa (del orden de 1 a 3 microsegundos), incluso para valores tan grandes como 90 o 120.
Esto se explica porque:
- Como vimos la versión recursiva básica realiza O(2ⁿ) llamadas. Con memoization, cada valor de Fibonacci se calcula solo una vez, por lo que la complejidad se reduce a O(n).
- El árbol recursivo se aplana y deja de crecer exponencialmente.
- Cada llamada revisa si el valor ya está calculado. Si ya está almacenado, devuelve el resultado en tiempo constante O(1) conviertiendo el algoritmo en algo casi idéntico a la versión iterativa.
- Aunque se utilice recursión, ahora se hacen solo n llamadas y casi todas retornan inmediatamente al encontrar el resultado memorizado.

Vemos entonces que ambas versiones optimizadas (iterativa y memoization) logran prácticamente el mismo rendimiento.


Implementar OpenMP aquí tampoco aporta beneficios: una vez aplicado memoization, la dependencia de datos entre los resultados parciales obliga a calcular los valores en orden creciente, y cada posición del arreglo debe estar completa antes de ser utilizada por otra. Por lo tanto, no existe paralelismo natural aprovechable sin rediseñar el algoritmo.


**Versión con Thresholding `fib_thresh.c`**


Se implementó la versión con thresholding aplicando OpenMP correspondientemente, para detalles de implementación se puede revisar el archivo `fib_thresh.c`.
Luego se analizaron los tiempos de ejecución, donde cada medición se repitió tres veces y se tomó el tiempo promedio, incluyendo su desviación estándar, 
variando tanto el `N` como `TH` (Threshold) del programa. Se obtuvieron los siguientes resultados:

<img width="1319" height="643" alt="image" src="https://github.com/user-attachments/assets/e51cbfa8-0cc7-4673-8973-81274e174936" />

Analizando el grafico se puede ver que cuanto menor es el TH (umbral), más rápido crece el tiempo de ejecución. 
Esto ocurre porque un TH chico implica que el programa sigue creando tasks recursivas hasta niveles muy profundos 
(como ocurría en la primera versión), generando demasiadas tareas para tasks muy sencillas que se traduce en un overhead enorme del runtime de OpenMP. 
En cambio, valores mayores de TH cortan antes la recursión paralela y delegan más trabajo a la parte secuencial iterativa, 
que como vimos en las versiones iterativas o de memoization es muchísimo más eficiente para este problema. 
Esto permite llegar a valores de N más grandes antes de que el tiempo se dispare. En resumen, el thresholding
demuestra que el problema de fibonacci no es el caso de uso para aplicar paralelismo, debido a que el overhead de creación y
administración de tasks termina siendo mucho mayor que el costo de resolver la operación secuencialmente.


## d) N-Reinas OpenMP  
_Ahora, dado el siguiente código secuencial (sin OpenMP) que describe el problema de las reinas:_
```c
#include <stdio.h>
#include <stdbool.h>
#define N 4
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
    solutions++;
    return;
  }
  for (int col = 0; col < N; col++) {
    if (is_safe(board, row, col)) {
      board[row] = col;
      solve(row + 1, board);
    }
  }
}
int main() {
  int board[N];
  solve(0, board);
  printf("Soluciones para %d reinas: %lld\n", N, solutions);
  return 0;
}
```
_Parametrizá el programa para que reciba por argumento de línea de comando el tamaño del tablero. 
Luego, pensá una solución con OpenMP utilizando las directivas que prefieras. Podés usar las del programa anterior de Fibonacci o cualquiera vista en teoría._

La versión paralela del problema de las N-Reinas se implementó utilizando tasks de OpenMP para que cada decisión del árbol de backtracking pueda ejecutarse en paralelo. 
En cada nivel de la recursión, cuando una reina puede colocarse en una columna válida, se genera una nueva tarea `#pragma omp task` que continúa explorando esa rama del árbol de soluciones.
Para evitar interferencias entre tareas y garantizar que cada rama trabaje con su propio estado, se copia el tablero y se pasa mediante `firstprivate`, 
asegurando que cada tarea tenga su propia versión independiente. 
Además, se utiliza `#pragma omp taskwait` para que cada llamada recursiva espere a que todas sus tareas hijas finalicen antes de volver. 
Como múltiples tareas pueden encontrar soluciones simultáneamente, la actualización del contador global se protegió con `#pragma omp atomic`, 
evitando condiciones de carrera al incrementar la variable solutions. De esta forma, se logra un paralelismo completo del árbol de búsqueda, 
análogo al paralelismo aplicado en la versión recursiva paralela de Fibonacci. Para más detalle de la implementación ver el archivo `queens_par.c`.

## e) N-Reinas Secuencial vs Completamente paralelizado

_Como en el caso de c), compará el tiempo del programa secuencial y el paralelo para distintos tamaños de tableros. 
Podés también utilizar distinto número de hilos si preferís. ¿Qué comportamiento observás?_

Para analizar el rendimiento se realizó una comparación entre la versión secuencial y la versión paralelizada con OpenMP. 
Para cada tamaño de tablero N se midió el tiempo de ejecución del programa secuencial y también del paralelo utilizando distintos números de hilos (1, 2, 4 y 8). 
Cada medición se repitió tres veces y se tomó el tiempo promedio, incluyendo su desviación estándar. Con esto se observo cómo escala el algoritmo en ambas versiones, 
y en particular que efecto tiene el “aumento del paralelismo” para esta implementación.

<img width="1656" height="890" alt="image" src="https://github.com/user-attachments/assets/832e566f-c49e-429f-8d88-0a7cf3d7776c" />

Al observar el gráfico, se ve que la versión paralela no sólo no mejora al algoritmo secuencial, 
sino que incluso empeora significativamente a medida que se aumentan los hilos. Si bien para N menores a 11 
las diferencias entre todas las versiones son mínimas, a partir de N=12 el tiempo empieza a crecer a mayor cantidad de hilos que se utilizan. 
En particular, con 8 hilos los tiempos crecen abruptamente debido a la enorme cantidad de tareas recursivas generadas y al costo de sincronización entre ellas, 
igual que ocurría para la primera versión de Fibonacci. En resumen, el experimento confirma que el paralelismo con tasks es altamente ineficiente 
para N-Reinas cuando se paraleliza todo el árbol por el overhead que incorpora OpenMP.

## f) N-Reinas optimizado con Thresholding

_Al igual que d), podés implementar una variante optimizada. Te sugiero thresholding. ¿Ves algún efecto positivo?_

Se implementó una versión híbrida del algoritmo, en la que solamente las primeras TH filas del árbol de búsqueda generan tareas paralelas. 
A partir de esa profundidad, el algoritmo continúa en forma secuencial. Este enfoque reduce drásticamente la cantidad de tasks extremadamente pequeñas,
'que en la versión totalmente paralela generaban un overhead considerable: el runtime de OpenMP pasaba más tiempo creando y administrando tareas que 
resolviendo el problema. Con thresholding, la parte superficial del árbol, que tiene pocas ramas pero alto potencial de paralelismo, se ejecuta en paralelo, 
mientras que la parte profunda, donde el número de nodos crece exponencialmente, se maneja secuencialmente, evitando explosiones combinatorias de tareas. Para mas detalles de implementacion
ver el archivo `queens_th.c`.

Para analizar el impacto del thresholding en la versión paralela del algoritmo de N-Reinas, se realizó un benchmark comparando la implementación secuencial con una variante paralela optimizada. 
La configuración utilizada fue la siguiente: tamaños de tablero `N = {10, 11, 12, 13, 14, 15}`, thresholds `TH = {1, 2, 3, 4}`, tres repeticiones por medición y utilización de 8 hilos en la versión paralela.
Al ver la notable diferencia entre secuencial y thresholding, por claridad del grafico se promediaron los tiempos obtenidos por los distintos valores de TH con su correspondiente desvío estándar, 
generando así una única curva representativa del comportamiento paralelo optimizado mediante thresholding. Luego, esta curva fue comparada contra la versión secuencial clásica a fin de evaluar 
el impacto real de la optimización.

<img width="1547" height="893" alt="image" src="https://github.com/user-attachments/assets/22a85121-2d36-4552-9053-c7125f89b3b5" />

El gráfico muestra claramente que el thresholding mejora sustancialmente el rendimiento, logrando superar al algoritmo secuencial en tamaños de tablero mas elevados. Para N<=12, ambas versiones son muy rápidas y las diferencias 
son mínimas debido al bajo costo computacional. Sin embargo, a partir de N=13 y especialmente en N=14 y N=15, la versión secuencial crece abruptamente, 
mientras que la versión paralela con thresholding mantiene tiempos mucho menores: el promedio entre distintos valores de TH se mantiene alrededor de 4 segundos en N=15, 
frente a más de 20 segundos de la versión secuencial. Esto confirma que limitar la paralelización a los primeros niveles del árbol reduce radicalmente la explosión de tareas, 
disminuye el overhead y permite aprovechar mejor los hilos disponibles, resultando en una mejora real de performance para N-Reinas. Esto es debido a que ahora si se justifica 
la creación de tasks para paralelizar carga ya que los primeros niveles del árbol para un N grande si requieren una cantidad considerable de computo.

Para analizar el efecto del parámetro threshold en la versión paralela del algoritmo de N-Reinas, 
se ejecutó un benchmark variando tanto el tamaño del tablero como el valor del umbral. La configuración 
utilizada fue la siguiente: se empleó la versión paralela con thresholding, evaluando tableros de tamaño 
`N = 10, 11, 12, 13, 14 , 15`, y comparando distintos valores de umbral `TH = 1, 3, 7, 8, 9, 10`. 
Cada combinación se ejecutó 3 veces. Todas las mediciones se realizaron utilizando 8 hilos de OpenMP.
<img width="1584" height="925" alt="image" src="https://github.com/user-attachments/assets/0b154ace-f796-420e-8fc2-208e96c916ea" />

El gráfico muestra cómo varía el tiempo de ejecución del algoritmo paralelo de N-Reinas utilizando distintos valores de threshold (TH), 
manteniendo constante la cantidad de hilos. El comportamiento observado es consistente con lo mencionado anteriormente en la versión totalmente paralela 
y la versión secuencial: thresholds mas pequeños producen mejores tiempos para N entre 12 y 15, debido a que permiten paralelizar un nivel más profundo del árbol de búsqueda 
sin generar una cantidad explosiva de tareas, justificando la paralelización de esas tareas. En contraste, thresholds grandes (TH>=8) empeoran drásticamente el rendimiento. 
Esto ocurre porque el paralelismo se limita a niveles muy superficiales del árbol, lo que vuelve a generar demasiado overhead de creación y administración de tasks, con tasks 
demasiado granulares, reduciendo el paralelismo útil y aumentando la carga de sincronización. El caso de TH=10 es el más desfavorable, la mayor parte del trabajo queda secuencial, 
resultando en un crecimiento abrupto del tiempo para N>=14.

En resumen, el gráfico ilustra que existe un equilibrio: thresholds bajos o intermedios proporcionan la mejor relación entre paralelismo y overhead,
mientras que valores demasiado grandes vuelven el algoritmo muy ineficiente al producir demasiadas tasks si el árbol es profundo. 
Elegir el TH adecuado es clave para obtener un rendimiento eficiente.

## g) Conclucion 

_Elaborá una conclusión acerca de lo realizado, tanto en codificación como en experimentación. 
¿Qué podés a partir de la aplicación de OpenMP en ambos códigos? ¿Fue beneficioso OpenMP para ambos casos, y por qué?_

La conclusión al respecto del uso de esta herramienta es que no siempre conviene paralelizar las tareas, a veces como vimos en el caso de Fibonacci, 
donde la tarea a paralelizar implica muy poco computo, no justifica la creación y administración de toda la lógica de paralelización ya que eso 
genera un costo de computo mayor que simplemente ejecutar todo de manera secuencial. Sin embargo cuando el algoritmo escala en tareas mas pesadas, 
como en el caso de N-Reinas con un N relativamente alto que genera que las tareas de los nodos de las primeras filas si sean mas pesadas en computo, 
entonces la paralelización de esas tareas pesadas si justifican el costo de paralelizar el codigo, resultando en una mayor eficiencia que el codigo secuencial. 
Metafóricamente es como si la paralelización fuera una especie de “costo fijo”, donde para justificarse se requiere cierto nivel de peso en el computo de la parte paralelizable, 
de lo contrario solo genera mas overhead que beneficios.


