"""
Genera los archivos de JFLAP (.jff) a partir de las MISMAS tablas δ que usa
el programa en Python. Así se garantiza que el autómata dibujado en JFLAP y
el autómata programado son exactamente el mismo.

Uso:   python generar_jflap.py
Salida:
  jflap/riego.jff      (Autómata Finito)
  jflap/bandejas.jff   (Autómata de Pila)

En JFLAP: File → Open → elegir el .jff.
  * Riego:    Input → Multiple Run (pegar las cadenas de prueba)
  * Bandejas: Input → Multiple Run → "Accept by final state"
"""

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

from automatas import riego, bandejas

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jflap")


def nuevo_automata(tipo):
    raiz = ET.Element("structure")
    ET.SubElement(raiz, "type").text = tipo
    return raiz, ET.SubElement(raiz, "automaton")


def agregar_estado(automata, id_estado, nombre, x, y, inicial, final):
    estado = ET.SubElement(automata, "state", {"id": str(id_estado), "name": nombre})
    ET.SubElement(estado, "x").text = f"{x:.1f}"
    ET.SubElement(estado, "y").text = f"{y:.1f}"
    if inicial:
        ET.SubElement(estado, "initial")
    if final:
        ET.SubElement(estado, "final")


def guardar(raiz, nombre_archivo):
    os.makedirs(CARPETA, exist_ok=True)
    texto = minidom.parseString(ET.tostring(raiz, encoding="utf-8"))
    ruta = os.path.join(CARPETA, nombre_archivo)
    with open(ruta, "wb") as archivo:
        archivo.write(texto.toprettyxml(indent="\t", encoding="UTF-8"))
    return ruta


def generar_riego():
    raiz, automata = nuevo_automata("fa")
    posiciones = {
        "q0": (100, 200), "q1": (300, 200), "q2": (500, 200),
        "q3": (500, 400), "qE": (300, 400),
    }
    ids = {nombre: i for i, nombre in enumerate(riego.ESTADOS)}

    for nombre, (x, y) in posiciones.items():
        agregar_estado(automata, ids[nombre], nombre, x, y,
                       inicial=nombre == riego.ESTADO_INICIAL,
                       final=nombre in riego.ESTADOS_FINALES)

    total = 0
    for origen, fila in riego.DELTA.items():
        for simbolo, destino in fila.items():
            t = ET.SubElement(automata, "transition")
            ET.SubElement(t, "from").text = str(ids[origen])
            ET.SubElement(t, "to").text = str(ids[destino])
            ET.SubElement(t, "read").text = simbolo
            total += 1

    ruta = guardar(raiz, "riego.jff")
    print(f"Generado {ruta}  ({len(ids)} estados, {total} transiciones)")


def generar_bandejas():
    raiz, automata = nuevo_automata("pda")
    posiciones = {"q0": (150, 200), "q1": (450, 200)}
    ids = {nombre: i for i, nombre in enumerate(bandejas.ESTADOS)}

    for nombre, (x, y) in posiciones.items():
        agregar_estado(automata, ids[nombre], nombre, x, y,
                       inicial=nombre == bandejas.ESTADO_INICIAL,
                       final=nombre in bandejas.ESTADOS_FINALES)

    for (origen, leido, tope), (destino, apilar) in bandejas.DELTA.items():
        t = ET.SubElement(automata, "transition")
        ET.SubElement(t, "from").text = str(ids[origen])
        ET.SubElement(t, "to").text = str(ids[destino])
        # En JFLAP, λ se representa con un elemento vacío
        lectura = ET.SubElement(t, "read")
        if leido != bandejas.LAMBDA:
            lectura.text = leido
        ET.SubElement(t, "pop").text = tope
        apilado = ET.SubElement(t, "push")
        if apilar:
            apilado.text = apilar

    ruta = guardar(raiz, "bandejas.jff")
    print(f"Generado {ruta}  ({len(ids)} estados, {len(bandejas.DELTA)} transiciones)")


if __name__ == "__main__":
    generar_riego()
    generar_bandejas()
