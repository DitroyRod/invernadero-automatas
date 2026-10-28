"""
Pruebas automáticas de los dos autómatas.

Correr con:   python -m unittest discover tests -v

Además de probar cadenas sueltas, se verifican dos equivalencias teóricas
probando TODAS las cadenas hasta cierta longitud:
  * AFD de riego  ≡  expresión regular obtenida por el lema de Arden
  * AP de bandejas ≡  gramática libre de contexto  S → tSTS | pSPS | λ
"""

import itertools
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automatas import riego, bandejas   # noqa: E402
import main                            # noqa: E402


# ---------------------------------------------------------------------------
# Expresión regular equivalente al AFD de riego (derivada con el lema de Arden)
#   R  = (h*s)*
#   ER = ( h | s (s | A R C)* ( h | A R h+ C ) )*
# ---------------------------------------------------------------------------
R = r"(?:h*s)*"
ER_RIEGO = re.compile(rf"(?:h|s(?:s|A{R}C)*(?:h|A{R}h+C))*")


# ---------------------------------------------------------------------------
# Reconocedor basado directamente en la gramática  S → tSTS | pSPS | λ
# (análisis descendente recursivo)
# ---------------------------------------------------------------------------
PAREJA = {"t": "T", "p": "P"}


def deriva_S(cadena):
    """True si S ⇒* cadena usando la gramática libre de contexto."""
    posicion = 0

    def S():
        nonlocal posicion
        # S → t S T S | p S P S   (mientras empiece una siembra)
        while posicion < len(cadena) and cadena[posicion] in PAREJA:
            cierre = PAREJA[cadena[posicion]]
            posicion += 1
            if not S():
                return False
            if posicion >= len(cadena) or cadena[posicion] != cierre:
                return False
            posicion += 1
        return True   # S → λ

    return S() and posicion == len(cadena)


class TestRiego(unittest.TestCase):

    def test_definicion_completa(self):
        """El AFD es completo: hay una transición por cada estado y símbolo."""
        for estado in riego.ESTADOS:
            self.assertEqual(set(riego.DELTA[estado]), set(riego.ALFABETO))

    def test_aceptadas(self):
        for cadena in ["", "h", "sh", "sAhC", "sAsshC", "sACAhC", "hsAhChsAhC"]:
            with self.subTest(cadena=cadena):
                self.assertTrue(riego.acepta(cadena))

    def test_rechazadas(self):
        for cadena in ["A", "hA", "C", "s", "sA", "sAh", "sAsC", "sAAhC", "sAhCC", "l", "x"]:
            with self.subTest(cadena=cadena):
                self.assertFalse(riego.acepta(cadena))

    def test_motivos(self):
        self.assertIn("sin haber detectado suelo seco", riego.procesar("A")["motivo"])
        self.assertIn("válvula abierta", riego.procesar("sA")["motivo"])
        self.assertIn("nunca se cerró", riego.procesar("sAh")["motivo"])

    def test_equivalente_a_expresion_regular(self):
        """Teorema de Kleene: AFD y ER describen el mismo lenguaje (|w| ≤ 8)."""
        for largo in range(9):
            for tupla in itertools.product("shAC", repeat=largo):
                w = "".join(tupla)
                self.assertEqual(riego.acepta(w), bool(ER_RIEGO.fullmatch(w)), w)


class TestBandejas(unittest.TestCase):

    def test_aceptadas(self):
        for cadena in ["", "tT", "tpPT", "tTpP", "ttpPTT", "tpPpPT"]:
            with self.subTest(cadena=cadena):
                self.assertTrue(bandejas.acepta(cadena))

    def test_rechazadas(self):
        for cadena in ["T", "tpTP", "tP", "ttT", "tTT", "p", "x"]:
            with self.subTest(cadena=cadena):
                self.assertFalse(bandejas.acepta(cadena))

    def test_motivos(self):
        self.assertIn("no hay bandejas", bandejas.procesar("T")["motivo"])
        self.assertIn("de arriba es de pimiento", bandejas.procesar("tpTP")["motivo"])
        self.assertIn("Quedaron 1", bandejas.procesar("ttT")["motivo"])

    def test_determinista(self):
        """AP determinista: si hay transición λ con (q, X) no hay otra con (q, a, X)."""
        for (q, a, X) in bandejas.DELTA:
            if a == bandejas.LAMBDA:
                for simbolo in bandejas.ALFABETO:
                    self.assertNotIn((q, simbolo, X), bandejas.DELTA)

    def test_equivalente_a_gramatica(self):
        """AP y gramática S → tSTS | pSPS | λ generan el mismo lenguaje (|w| ≤ 8)."""
        for largo in range(9):
            for tupla in itertools.product("tpTP", repeat=largo):
                w = "".join(tupla)
                self.assertEqual(bandejas.acepta(w), deriva_S(w), w)

    def test_tn_Tn(self):
        """La familia tⁿTⁿ (la del lema de bombeo) se acepta para n grandes."""
        for n in (1, 10, 100, 1000):
            self.assertTrue(bandejas.acepta("t" * n + "T" * n))
            self.assertFalse(bandejas.acepta("t" * n + "T" * (n - 1)))


class TestArchivoDePruebas(unittest.TestCase):

    def test_cadenas_de_prueba_txt(self):
        modulos = {"riego": riego, "bandejas": bandejas}
        for automata, cadena, esperado, comentario in main.leer_pruebas():
            with self.subTest(automata=automata, cadena=cadena, nota=comentario):
                self.assertEqual(modulos[automata].acepta(cadena), esperado)


if __name__ == "__main__":
    unittest.main()
