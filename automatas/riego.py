"""
Autómata Finito Determinista (AFD) — Controlador de riego automático
=====================================================================

Problema
--------
Un sistema de riego registra durante el día las lecturas de sus sensores
y las acciones que hace sobre la válvula. El autómata recibe ese registro
como una cadena y decide si el riego se hizo correctamente.

Reglas del riego correcto
  1. La válvula solo se abre si antes se detectó suelo seco.
  2. Si el suelo se humedece mientras riega, hay que cerrar.
  3. No se puede abrir una válvula abierta ni cerrar una cerrada.
  4. El día termina con la válvula cerrada y sin suelo seco pendiente.

Definición formal   M1 = (Q, Σ, δ, q0, F)
  Q  = {q0, q1, q2, q3, qE}
  Σ  = {s, h, A, C}
  q0 = estado inicial
  F  = {q0}
  δ  = tabla DELTA (más abajo)

Tipo 3 de la jerarquía de Chomsky (lenguaje regular): para decidir solo
hace falta recordar la situación ACTUAL (válvula abierta/cerrada y si el
suelo está seco), que es una cantidad finita de información.
"""

# ---------------------------------------------------------------------------
# Σ : alfabeto de entrada
# ---------------------------------------------------------------------------
ALFABETO = {
    "s": "sensor: suelo seco",
    "h": "sensor: suelo húmedo",
    "A": "acción: abrir válvula",
    "C": "acción: cerrar válvula",
}

# ---------------------------------------------------------------------------
# Q : conjunto de estados (con su significado en el sistema real)
# ---------------------------------------------------------------------------
ESTADOS = {
    "q0": "En espera (válvula cerrada, suelo bien)",
    "q1": "Suelo seco detectado (hay que regar)",
    "q2": "Regando (válvula abierta)",
    "q3": "Hay que cerrar (el suelo ya está húmedo)",
    "qE": "Error (estado trampa)",
}

ESTADO_INICIAL = "q0"
ESTADOS_FINALES = {"q0"}

# ---------------------------------------------------------------------------
# δ : Q × Σ → Q   (función de transición, idéntica a la tabla del informe)
# ---------------------------------------------------------------------------
DELTA = {
    #        s           h           A           C
    "q0": {"s": "q1", "h": "q0", "A": "qE", "C": "qE"},
    "q1": {"s": "q1", "h": "q0", "A": "q2", "C": "qE"},
    "q2": {"s": "q2", "h": "q3", "A": "qE", "C": "q1"},
    "q3": {"s": "q2", "h": "q3", "A": "qE", "C": "q0"},
    "qE": {"s": "qE", "h": "qE", "A": "qE", "C": "qE"},
}

# Explicación de cada transición que lleva al estado trampa
MOTIVOS_ERROR = {
    ("q0", "A"): "Se abrió la válvula sin haber detectado suelo seco",
    ("q0", "C"): "Se cerró una válvula que ya estaba cerrada",
    ("q1", "C"): "Se cerró una válvula que ya estaba cerrada",
    ("q2", "A"): "Se abrió una válvula que ya estaba abierta",
    ("q3", "A"): "Se abrió una válvula que ya estaba abierta",
}

# Explicación de terminar en un estado que no es final
MOTIVOS_FIN = {
    "q1": "El día terminó con el suelo seco y sin regar",
    "q2": "El día terminó con la válvula abierta",
    "q3": "El suelo ya estaba húmedo, pero la válvula nunca se cerró",
}


def procesar(cadena):
    """
    Procesa la cadena símbolo por símbolo, como lo hace el AFD.

    Devuelve un diccionario con:
      aceptada : True / False
      pasos    : lista de (estado_actual, símbolo, estado_siguiente)
      final    : estado en el que terminó
      motivo   : explicación del resultado
    """
    estado = ESTADO_INICIAL
    pasos = []
    primer_error = None

    for simbolo in cadena:
        # Si el símbolo no está en Σ, la cadena no pertenece al lenguaje
        if simbolo not in ALFABETO:
            return {
                "aceptada": False,
                "pasos": pasos,
                "final": estado,
                "motivo": f"El símbolo '{simbolo}' no pertenece al alfabeto Σ",
            }

        siguiente = DELTA[estado][simbolo]          # aplicar δ(estado, símbolo)
        pasos.append((estado, simbolo, siguiente))

        # Guardar el primer error para explicarlo al final
        if siguiente == "qE" and primer_error is None:
            primer_error = MOTIVOS_ERROR[(estado, simbolo)]

        estado = siguiente

    # Al terminar la cadena: se acepta si el estado actual pertenece a F
    if estado in ESTADOS_FINALES:
        motivo = "Riego correcto: válvula cerrada y suelo bien"
        return {"aceptada": True, "pasos": pasos, "final": estado, "motivo": motivo}

    motivo = primer_error if estado == "qE" else MOTIVOS_FIN[estado]
    return {"aceptada": False, "pasos": pasos, "final": estado, "motivo": motivo}


def acepta(cadena):
    """Atajo: True si la cadena pertenece al lenguaje L(M1)."""
    return procesar(cadena)["aceptada"]
