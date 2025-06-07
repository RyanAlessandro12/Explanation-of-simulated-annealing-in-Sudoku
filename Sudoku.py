import random
import numpy as np
import math 
from random import choice
import statistics 

sudokuInicial = """
        000000100
        150009000
        629000500
        865420300
        000900780
        000003000
        900700805
        030500200
        500000074
                """

sudoku = np.array([[int(i) for i in linea] for linea in sudokuInicial.split()])

def imprimirSudoku(sudoku):
    print("\n")
    for i in range(len(sudoku)):
        linea = ""
        if i == 3 or i == 6:
            print("---------------------")
        for j in range(len(sudoku[i])):
            if j == 3 or j == 6:
                linea += "| "
            linea += str(sudoku[i,j]) + " "
        print(linea)

def fijarValoresSudoku(sudokuFijo):
    for i in range(9):
        for j in range(9):
            if sudokuFijo[i,j] != 0:
                sudokuFijo[i,j] = 1
    return sudokuFijo

def calcularErroresTotales(sudoku):
    errores = 0 
    for i in range(9):
        errores += calcularErroresFilaColumna(i, i, sudoku)
    return errores

def calcularErroresFilaColumna(fila, columna, sudoku):
    errores = (9 - len(np.unique(sudoku[:,columna]))) + (9 - len(np.unique(sudoku[fila,:])))
    return errores

def crearListaBloques3x3():
    listaFinal = []
    for r in range(9):
        bloque = []
        bloqueFilas = [i + 3*(r % 3) for i in range(3)]
        bloqueColumnas = [i + 3*(r // 3) for i in range(3)]
        for x in bloqueFilas:
            for y in bloqueColumnas:
                bloque.append([x, y])
        listaFinal.append(bloque)
    return listaFinal

def llenarBloquesAleatoriamente(sudoku, listaBloques):
    for bloque in listaBloques:
        for casilla in bloque:
            if sudoku[casilla[0], casilla[1]] == 0:
                bloqueActual = sudoku[bloque[0][0]:(bloque[-1][0]+1), bloque[0][1]:(bloque[-1][1]+1)]
                sudoku[casilla[0], casilla[1]] = choice([i for i in range(1, 10) if i not in bloqueActual])
    return sudoku

def sumaBloque(sudoku, bloque):
    return sum(sudoku[casilla[0], casilla[1]] for casilla in bloque)

def dosCasillasAleatoriasEnBloque(sudokuFijo, bloque):
    while True:
        primera = random.choice(bloque)
        segunda = choice([c for c in bloque if c is not primera])
        if sudokuFijo[primera[0], primera[1]] != 1 and sudokuFijo[segunda[0], segunda[1]] != 1:
            return [primera, segunda]

def intercambiarCasillas(sudoku, casillas):
    sudokuPropuesto = np.copy(sudoku)
    a, b = casillas
    sudokuPropuesto[a[0], a[1]], sudokuPropuesto[b[0], b[1]] = sudokuPropuesto[b[0], b[1]], sudokuPropuesto[a[0], a[1]]
    return sudokuPropuesto

def estadoPropuesto(sudoku, sudokuFijo, listaBloques):
    bloqueAleatorio = random.choice(listaBloques)
    if sumaBloque(sudokuFijo, bloqueAleatorio) > 6:
        return (sudoku, 1, 1)
    casillas = dosCasillasAleatoriasEnBloque(sudokuFijo, bloqueAleatorio)
    sudokuPropuesto = intercambiarCasillas(sudoku, casillas)
    return [sudokuPropuesto, casillas]

def elegirNuevoEstado(sudokuActual, sudokuFijo, listaBloques, sigma):
    propuesta = estadoPropuesto(sudokuActual, sudokuFijo, listaBloques)
    nuevoSudoku = propuesta[0]
    casillas = propuesta[1]
    costoActual = calcularErroresFilaColumna(casillas[0][0], casillas[0][1], sudokuActual) + \
                  calcularErroresFilaColumna(casillas[1][0], casillas[1][1], sudokuActual)
    nuevoCosto = calcularErroresFilaColumna(casillas[0][0], casillas[0][1], nuevoSudoku) + \
                 calcularErroresFilaColumna(casillas[1][0], casillas[1][1], nuevoSudoku)
    diferencia = nuevoCosto - costoActual
    rho = math.exp(-diferencia / sigma) if sigma > 0 else 0
    if np.random.uniform(0, 1) < rho:
        return [nuevoSudoku, diferencia]
    return [sudokuActual, 0]

def elegirNumeroIteraciones(sudokuFijo):
    return np.count_nonzero(sudokuFijo)

def calcularSigmaInicial(sudoku, sudokuFijo, listaBloques):
    diferencias = []
    tmpSudoku = sudoku
    for _ in range(10):
        tmpSudoku = estadoPropuesto(tmpSudoku, sudokuFijo, listaBloques)[0]
        diferencias.append(calcularErroresTotales(tmpSudoku))
    return statistics.pstdev(diferencias)

def resolverSudoku(sudoku):
    solucionEncontrada = False
    while not solucionEncontrada:
        factorReduccion = 0.99
        ciclosEstancado = 0
        sudokuFijo = np.copy(sudoku)
        imprimirSudoku(sudoku)
        fijarValoresSudoku(sudokuFijo)
        listaBloques = crearListaBloques3x3()
        tmpSudoku = llenarBloquesAleatoriamente(sudoku, listaBloques)
        sigma = calcularSigmaInicial(sudoku, sudokuFijo, listaBloques)
        puntaje = calcularErroresTotales(tmpSudoku)
        iteraciones = elegirNumeroIteraciones(sudokuFijo)

        if puntaje <= 0:
            solucionEncontrada = True

        while not solucionEncontrada:
            puntajeAnterior = puntaje
            for _ in range(iteraciones):
                nuevoEstado = elegirNuevoEstado(tmpSudoku, sudokuFijo, listaBloques, sigma)
                tmpSudoku = nuevoEstado[0]
                diferencia = nuevoEstado[1]
                puntaje += diferencia
                print("Puntaje:", puntaje)

                if puntaje <= 0:
                    solucionEncontrada = True
                    break

            sigma *= factorReduccion
            if puntaje <= 0:
                solucionEncontrada = True
                break
            if puntaje >= puntajeAnterior:
                ciclosEstancado += 1
            else:
                ciclosEstancado = 0
            if ciclosEstancado > 80:
                sigma += 2
            if calcularErroresTotales(tmpSudoku) == 0:
                imprimirSudoku(tmpSudoku)
                break

    return tmpSudoku

solucion = resolverSudoku(sudoku)
print("\nErrores finales:", calcularErroresTotales(solucion))
imprimirSudoku(solucion)
