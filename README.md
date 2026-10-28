# Sistema de Gestión de Invernadero 🌱

Trabajo final integrador de **Fundamentos Teóricos de la Informática**.
Autor: Brian Rodriguez

Se modelan dos problemas reales de un invernadero con dos aceptores
de distintos niveles de la **jerarquía de Chomsky**:

| Sistema | Autómata | Tipo de Chomsky | Por qué |
|---|---|---|---|
| Riego automático | Autómata Finito Determinista (AFD) | Tipo 3 · Regular | Solo necesita recordar la situación **actual** (información finita) |
| Bandejas de plantines apiladas | Autómata de Pila determinista (AP) | Tipo 2 · Libre de contexto | Necesita recordar **todas** las bandejas en orden, sin límite |

---

## 1. Riego automático (AFD)

Valida el registro diario de un sistema de riego.

**M₁ = (Q, Σ, δ, q0, F)**

- Q = {q0, q1, q2, q3, qE}
- Σ = {s, h, A, C}: `s` suelo seco · `h` suelo húmedo · `A` abrir válvula · `C` cerrar válvula
- q0 = estado inicial
- F = {q0}

| δ | s | h | A | C |
|---|---|---|---|---|
| →\*q0 (en espera) | q1 | q0 | qE | qE |
| q1 (suelo seco) | q1 | q0 | q2 | qE |
| q2 (regando) | q2 | q3 | qE | q1 |
| q3 (hay que cerrar) | q2 | q3 | qE | q0 |
| qE (error) | qE | qE | qE | qE |

**Gramática regular equivalente**

```
Q0 → hQ0 | sQ1 | λ
Q1 → sQ1 | hQ0 | AQ2
Q2 → sQ2 | hQ3 | CQ1
Q3 → hQ3 | sQ2 | CQ0
```

**Expresión regular equivalente** (obtenida con el lema de Arden)

```
R  = (h*s)*
ER = ( h + s (s + A R C)* ( h + A R h⁺ C ) )*
```

Ejemplos: `sAhC` ✅ · `sACAhC` ✅ · `A` ❌ · `sA` ❌ · `sAh` ❌

## 2. Bandejas de plantines (AP)

Las bandejas de almácigos se apilan en el invernadero y solo se puede sacar
la de arriba. Valida que las siembras y trasplantes sigan un orden posible.

**M₂ = (Q, Σ, Γ, δ, q0, Z, F)**

- Q = {q0, q1}
- Σ = {t, p, T, P}: `t`/`p` sembrar tomate/pimiento · `T`/`P` trasplantar tomate/pimiento
- Γ = {Z, t, p}
- q0 = estado inicial, Z = fondo de la pila
- F = {q0} (acepta por estado final)

| Estado | Lee | Tope | → Estado | Apila |
|---|---|---|---|---|
| q0 | t | Z | q1 | tZ |
| q0 | p | Z | q1 | pZ |
| q1 | t | t | q1 | tt |
| q1 | t | p | q1 | tp |
| q1 | p | t | q1 | pt |
| q1 | p | p | q1 | pp |
| q1 | T | t | q1 | λ |
| q1 | P | p | q1 | λ |
| q1 | λ | Z | q0 | Z |

**Gramática libre de contexto equivalente**

```
S → t S T S | p S P S | λ
```

Ejemplos: `tpPT` ✅ · `tTpP` ✅ · `tpTP` ❌ · `ttT` ❌ · `T` ❌

---

## Estructura del repositorio

```
automatas/
  riego.py          AFD de riego (tabla δ + simulación)
  bandejas.py       AP de bandejas (tabla δ + simulación con pila)
main.py             Programa de consola (menú, trazas paso a paso)
generar_jflap.py    Genera los .jff de JFLAP desde las mismas tablas δ
jflap/
  riego.jff         Autómata finito para JFLAP
  bandejas.jff      Autómata de pila para JFLAP
cadenas_de_prueba.txt   Cadenas aceptadas y rechazadas
tests/              Pruebas automáticas
docs/index.html     Simulador web visual (GitHub Pages)
```

## Cómo usarlo

Requiere Python 3.8 o superior (sin librerías externas).

```bash
python main.py                    # menú interactivo
python main.py riego sAhC         # traza paso a paso de una cadena
python main.py bandejas tpPT
python main.py pruebas            # corre todas las cadenas de prueba
python -m unittest discover tests -v
python generar_jflap.py           # regenera los .jff
```

Las pruebas automáticas, además de las cadenas de ejemplo, verifican:

- que el AFD y la expresión regular aceptan exactamente las mismas cadenas (todas las de longitud ≤ 8);
- que el AP y la gramática libre de contexto aceptan exactamente las mismas cadenas (todas las de longitud ≤ 8);
- que el AP es determinista.

**JFLAP:** `File → Open` → `jflap/riego.jff` o `jflap/bandejas.jff`, y después
`Input → Multiple Run` para probar varias cadenas. En el autómata de pila,
elegir *Accept by final state*.

**Simulador web:** abrir `docs/index.html` en el navegador o publicarlo con
GitHub Pages (Settings → Pages → carpeta `/docs`).
