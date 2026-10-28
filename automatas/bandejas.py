"""
Autómata de Pila (AP) — Bandejas de plantines apiladas en el invernadero
=========================================================================

Problema
--------
En el invernadero las bandejas de almácigos se apilan una arriba de la
otra y solo se puede sacar la de arriba. Cada vez que se siembra una
bandeja se pone arriba de la pila; cada vez que se trasplanta, se saca
la de arriba. El autómata valida que la secuencia de siembras y
trasplantes sea posible y que al final no quede ninguna bandeja.

Alfabeto (minúscula = sembrar, mayúscula = trasplantar)
  t = sembrar bandeja de tomate      T = trasplantar tomate
  p = sembrar bandeja de pimiento    P = trasplantar pimiento

Definición formal   M2 = (Q, Σ, Γ, δ, q0, Z, F)
  Q  = {q0, q1}
  Σ  = {t, p, T, P}
  Γ  = {Z, t, p}        (Z = fondo de la pila)
  q0 = estado inicial
  Z  = símbolo inicial de la pila
  F  = {q0}
  δ  = tabla DELTA (más abajo)

Gramática libre de contexto equivalente
  S → t S T S | p S P S | λ

Tipo 2 de la jerarquía de Chomsky (lenguaje libre de contexto): hay que
recordar TODAS las bandejas apiladas y en orden, y la cantidad no tiene
límite. Un autómata finito no puede hacerlo (lema de bombeo con tⁿTⁿ).
Además es un AP DETERMINISTA: en cada situación hay a lo sumo una
transición posible.
"""

LAMBDA = "λ"
FONDO = "Z"

# ---------------------------------------------------------------------------
# Σ : alfabeto de entrada
# ---------------------------------------------------------------------------
ALFABETO = {
    "t": "sembrar bandeja de tomate",
    "p": "sembrar bandeja de pimiento",
    "T": "trasplantar tomate",
    "P": "trasplantar pimiento",
}

# Γ : alfabeto de la pila
ALFABETO_PILA = {FONDO: "fondo de la pila", "t": "bandeja de tomate", "p": "bandeja de pimiento"}

# Q : estados
ESTADOS = {
    "q0": "Invernadero sin bandejas",
    "q1": "Hay bandejas apiladas",
}

ESTADO_INICIAL = "q0"
ESTADOS_FINALES = {"q0"}

# ---------------------------------------------------------------------------
# δ : (estado, símbolo leído o λ, tope de la pila) → (nuevo estado, se apila)
#
# "se apila" es la cadena que reemplaza al tope; su primer carácter queda
# arriba. Ejemplo: ("q1", "t", "p") → ("q1", "tp") significa: leo t, saco p
# del tope y apilo "tp", o sea, la t queda arriba de la p.
# Una cadena vacía "" significa desapilar (pop).
# ---------------------------------------------------------------------------
DELTA = {
    # Primera siembra: el invernadero estaba vacío
    ("q0", "t", "Z"): ("q1", "tZ"),
    ("q0", "p", "Z"): ("q1", "pZ"),
    # Siembras siguientes: apilar arriba de lo que haya
    ("q1", "t", "t"): ("q1", "tt"),
    ("q1", "t", "p"): ("q1", "tp"),
    ("q1", "p", "t"): ("q1", "pt"),
    ("q1", "p", "p"): ("q1", "pp"),
    # Trasplantes: solo si la bandeja de arriba es de esa variedad
    ("q1", "T", "t"): ("q1", ""),
    ("q1", "P", "p"): ("q1", ""),
    # Se trasplantó la última bandeja: volver a "sin bandejas" (sin leer)
    ("q1", LAMBDA, "Z"): ("q0", "Z"),
}

NOMBRE = {"t": "tomate", "p": "pimiento", "T": "tomate", "P": "pimiento"}


def _motivo_bloqueo(estado, simbolo, tope):
    """Explica por qué no existe transición para (estado, símbolo, tope)."""
    if tope == FONDO:
        return f"Se intentó trasplantar {NOMBRE[simbolo]} pero no hay bandejas"
    return (f"Se intentó trasplantar {NOMBRE[simbolo]} pero la bandeja "
            f"de arriba es de {NOMBRE[tope]}")


def procesar(cadena):
    """
    Simula el AP sobre la cadena.

    La pila se guarda como una lista de Python con el TOPE AL FINAL.

    Devuelve un diccionario con:
      aceptada : True / False
      pasos    : lista de (estado, leído, tope, nuevo_estado, apilado, pila_resultante)
      final    : estado en el que terminó
      pila     : contenido final de la pila (de abajo hacia arriba)
      motivo   : explicación del resultado
    """
    estado = ESTADO_INICIAL
    pila = [FONDO]
    pasos = []
    i = 0

    def aplicar(leido, transicion):
        nonlocal estado
        tope = pila.pop()                       # sacar el tope
        nuevo_estado, apilar = transicion
        for simbolo_pila in reversed(apilar):   # apilar (el 1.º queda arriba)
            pila.append(simbolo_pila)
        pasos.append((estado, leido, tope, nuevo_estado,
                      apilar if apilar else LAMBDA, "".join(pila)))
        estado = nuevo_estado

    while True:
        tope = pila[-1]

        # 1) ¿Hay una transición λ (que no consume entrada)?
        if (estado, LAMBDA, tope) in DELTA:
            aplicar(LAMBDA, DELTA[(estado, LAMBDA, tope)])
            continue

        # 2) ¿Se terminó la cadena?
        if i == len(cadena):
            break

        simbolo = cadena[i]
        if simbolo not in ALFABETO:
            return {"aceptada": False, "pasos": pasos, "final": estado,
                    "pila": "".join(pila),
                    "motivo": f"El símbolo '{simbolo}' no pertenece al alfabeto Σ"}

        # 3) ¿Hay transición leyendo este símbolo con este tope?
        clave = (estado, simbolo, tope)
        if clave not in DELTA:
            # El AP se bloquea: no hay movimiento posible → rechaza
            return {"aceptada": False, "pasos": pasos, "final": estado,
                    "pila": "".join(pila),
                    "motivo": _motivo_bloqueo(estado, simbolo, tope)}

        aplicar(simbolo, DELTA[clave])
        i += 1

    # Se leyó toda la cadena: acepta por estado final
    if estado in ESTADOS_FINALES:
        return {"aceptada": True, "pasos": pasos, "final": estado,
                "pila": "".join(pila),
                "motivo": "Todas las bandejas se trasplantaron en un orden posible"}

    pendientes = [NOMBRE[b] for b in reversed(pila) if b != FONDO]
    return {"aceptada": False, "pasos": pasos, "final": estado,
            "pila": "".join(pila),
            "motivo": f"Quedaron {len(pendientes)} bandeja(s) sin trasplantar "
                      f"(de arriba hacia abajo: {', '.join(pendientes)})"}


def acepta(cadena):
    """Atajo: True si la cadena pertenece al lenguaje L(M2)."""
    return procesar(cadena)["aceptada"]
