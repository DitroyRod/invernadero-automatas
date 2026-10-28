"""
Sistema de Gestión de Invernadero — Fundamentos Teóricos de la Informática
==========================================================================

Programa de consola para probar los dos autómatas:
  1. Riego automático           → Autómata Finito Determinista (Tipo 3)
  2. Bandejas de plantines      → Autómata de Pila (Tipo 2)

Uso:
  python main.py                       (menú interactivo)
  python main.py riego sAhC            (probar una cadena directamente)
  python main.py bandejas tpPT
  python main.py pruebas               (correr cadenas_de_prueba.txt)
"""

import os
import sys

from automatas import riego, bandejas

# Para que los acentos y símbolos se vean bien en la consola de Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

ARCHIVO_PRUEBAS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "cadenas_de_prueba.txt")


def linea(caracter="─", largo=64):
    print(caracter * largo)


def mostrar_resultado(r):
    linea()
    if r["aceptada"]:
        print(f"  ✅ ACEPTA — {r['motivo']}")
    else:
        print(f"  ❌ RECHAZA — {r['motivo']}")
    linea()


def probar_riego(cadena):
    print(f"\nAFD de riego — cadena: {cadena if cadena else 'λ (vacía)'}")
    linea()
    print(f"  {'Paso':<5} {'Estado':<7} {'Lee':<4} {'→ Siguiente':<12} Significado")
    r = riego.procesar(cadena)
    print(f"  {'0':<5} {riego.ESTADO_INICIAL:<7} {'':<4} {'':<12} "
          f"{riego.ESTADOS[riego.ESTADO_INICIAL]}")
    for n, (actual, simbolo, siguiente) in enumerate(r["pasos"], start=1):
        print(f"  {n:<5} {actual:<7} {simbolo:<4} {'→ ' + siguiente:<12} "
              f"{riego.ESTADOS[siguiente]}")
    mostrar_resultado(r)
    return r


def probar_bandejas(cadena):
    print(f"\nAP de bandejas — cadena: {cadena if cadena else 'λ (vacía)'}")
    linea()
    print(f"  {'Paso':<5} {'Estado':<7} {'Lee':<4} {'Tope':<5} {'→ Estado':<9} "
          f"{'Apila':<6} Pila (abajo → arriba)")
    r = bandejas.procesar(cadena)
    print(f"  {'0':<5} {bandejas.ESTADO_INICIAL:<7} {'':<4} {'':<5} {'':<9} {'':<6} Z")
    for n, (est, leido, tope, nuevo, apilado, pila) in enumerate(r["pasos"], start=1):
        print(f"  {n:<5} {est:<7} {leido:<4} {tope:<5} {'→ ' + nuevo:<9} "
              f"{apilado:<6} {pila}")
    mostrar_resultado(r)
    return r


def leer_pruebas():
    """Lee cadenas_de_prueba.txt y devuelve (automata, cadena, esperado, comentario)."""
    pruebas = []
    with open(ARCHIVO_PRUEBAS, encoding="utf-8") as archivo:
        for renglon in archivo:
            renglon = renglon.strip()
            if not renglon or renglon.startswith("#"):
                continue
            datos, _, comentario = renglon.partition("#")
            automata, cadena, esperado = datos.split()
            cadena = "" if cadena == "-" else cadena
            pruebas.append((automata, cadena, esperado == "ACEPTA", comentario.strip()))
    return pruebas


def correr_pruebas():
    modulos = {"riego": riego, "bandejas": bandejas}
    pruebas = leer_pruebas()
    correctas = 0
    print()
    print(f"  {'Autómata':<9} {'Cadena':<12} {'Esperado':<9} {'Obtenido':<9} OK  Motivo")
    linea("─", 100)
    for automata, cadena, esperado, _ in pruebas:
        r = modulos[automata].procesar(cadena)
        ok = r["aceptada"] == esperado
        correctas += ok
        print(f"  {automata:<9} {cadena or 'λ':<12} "
              f"{'ACEPTA' if esperado else 'RECHAZA':<9} "
              f"{'ACEPTA' if r['aceptada'] else 'RECHAZA':<9} "
              f"{'✔' if ok else '✘':<3} {r['motivo']}")
    linea("─", 100)
    print(f"  Resultado: {correctas}/{len(pruebas)} pruebas correctas\n")
    return correctas == len(pruebas)


def menu():
    while True:
        print()
        linea("═")
        print("  SISTEMA DE GESTIÓN DE INVERNADERO — Autómatas (FTI)")
        linea("═")
        print("  1. Riego automático        (Autómata Finito Determinista)")
        print("     s=seco  h=húmedo  A=abrir  C=cerrar")
        print("  2. Bandejas de plantines   (Autómata de Pila)")
        print("     t/p=sembrar tomate/pimiento  T/P=trasplantar")
        print("  3. Correr todas las cadenas de prueba")
        print("  0. Salir")
        opcion = input("\n  Opción: ").strip()

        if opcion == "1":
            probar_riego(input("  Cadena (Enter = vacía): ").strip())
        elif opcion == "2":
            probar_bandejas(input("  Cadena (Enter = vacía): ").strip())
        elif opcion == "3":
            correr_pruebas()
        elif opcion == "0":
            break
        else:
            print("  Opción inválida")


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    if not argumentos:
        menu()
    elif argumentos[0] == "pruebas":
        sys.exit(0 if correr_pruebas() else 1)
    elif argumentos[0] in ("riego", "bandejas"):
        cadena = argumentos[1] if len(argumentos) > 1 else ""
        (probar_riego if argumentos[0] == "riego" else probar_bandejas)(cadena)
    else:
        print(__doc__)
