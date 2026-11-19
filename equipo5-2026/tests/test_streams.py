"""Pruebas de src/streams.py.
Ejecutación:
    python -m unittest discover tests
    python -m pytest tests/
"""
# pylint: disable=missing-class-docstring,missing-function-docstring

import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from itertools import islice
from unittest.mock import patch

from src.streams import (
    Evento,
    con_pausa,
    es_valido,
    fila_a_evento,
    filtrar_rango,
    formatear,
    generar_precios_btc,
    generar_precios_csv,
    leer_filas,
)

UTC = timezone.utc


def utc(*args):
    """Atajo para crear un datetime en UTC."""
    return datetime(*args, tzinfo=UTC)


def evento_en(minuto, precio=69.0):
    """Crea un Evento de prueba el 2021-01-01 a las 00:<minuto>."""
    return Evento(utc(2021, 1, 1, 0, minuto), "BTC", precio)


class PruebasConCsv(unittest.TestCase):
    """Clase base: ofrece una carpeta temporal para crear CSV de prueba."""

    def setUp(self):
        self._carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(self._carpeta.cleanup)

    def escribir_csv(self, contenido):
        """Guarda `contenido` en un CSV temporal y devuelve su ruta."""
        ruta = os.path.join(self._carpeta.name, "datos.csv")
        with open(ruta, "w", newline="", encoding="utf-8") as archivo:
            archivo.write(contenido)
        return ruta


# ---------------------------------------------------------------------------
# Evento y funciones puras
# ---------------------------------------------------------------------------

class TestEventoYFormato(unittest.TestCase):
    def test_evento_es_inmutable_y_se_formatea_con_fecha_miles_y_dos_decimales(self):
        evento = Evento(utc(2017, 8, 17, 4, 0, 0), "BTC", 1943.9)
        self.assertEqual(formatear(evento), "[2017-08-17 04:00:00] Precio BTC: 1,943.90")
        with self.assertRaises(AttributeError):
            setattr(evento, "precio", 1.0)  # setattr: el editor no marca error


class TestFilaAEvento(unittest.TestCase):
    def test_fila_valida_se_convierte_en_evento_utc_con_precio_redondeado(self):
        fila = {"datetime": "2017-08-17 04:00:00+00:00", "close": "69.6913"}
        evento = fila_a_evento("BTC", fila)
        self.assertEqual(evento, Evento(utc(2017, 8, 17, 4, 0, 0), "BTC", 69.69))
        assert evento is not None  # le dice al editor que ya no es None
        self.assertEqual(evento.timestamp.utcoffset(), timedelta(0))

    def test_fila_con_datos_invalidos_devuelve_none(self):
        valida = "2017-08-17 04:00:00+00:00"
        filas = [
            {"close": "67"},                                  # falta la fecha
            {"datetime": valida},                             # falta el precio
            {"datetime": valida, "close": "abc"},             # precio no numérico
            {"datetime": valida, "close": ""},                # precio vacío
            {"datetime": valida, "close": None},              # fila incompleta
            {"datetime": "no es fecha", "close": "13"},       # fecha inválida
        ]
        for fila in filas:
            with self.subTest(fila=fila):
                self.assertIsNone(fila_a_evento("BTC", fila))


class TestEsValido(unittest.TestCase):
    def test_solo_acepta_eventos_con_precio_positivo(self):
        self.assertTrue(es_valido(evento_en(0, 91.0)))
        self.assertFalse(es_valido(None))
        self.assertFalse(es_valido(evento_en(0, 0.0)))
        self.assertFalse(es_valido(evento_en(0, -67.0)))
        self.assertFalse(es_valido(evento_en(0, float("nan"))))


# ---------------------------------------------------------------------------
# Lectura del CSV
# ---------------------------------------------------------------------------

class TestLeerFilas(PruebasConCsv):
    def test_lee_filas_como_diccionarios_de_forma_perezosa(self):
        contenido = "\ufeffdatetime,close\r\n2021-01-01 00:00:00+00:00,69\r\n"
        flujo = leer_filas(self.escribir_csv(contenido))
        self.assertNotIsInstance(flujo, list)
        self.assertEqual(list(flujo), [{"datetime": "2021-01-01 00:00:00+00:00", "close": "69"}])

    def test_archivo_inexistente_lanza_error(self):
        with self.assertRaises(FileNotFoundError):
            list(leer_filas("no_existe_777.csv"))


class TestGenerarPreciosCsv(PruebasConCsv):
    CSV = (
        "timestamp,open,high,low,close,volume,datetime\r\n"
        "1609459200000,67,67,67,67,1,2021-01-01 00:00:00+00:00\r\n"
        "1609459260000,67,67,67,69.5,1,2021-01-01 00:01:00+00:00\r\n"
        "1609459320000,67,67,67,91,1,2021-01-01 00:02:00+00:00\r\n"
        "1609459380000,67,67,67,1943,1,2021-01-01 00:03:00+00:00\r\n"
    )

    def test_produce_un_evento_por_fila_con_close_como_precio_y_en_orden(self):
        eventos = list(generar_precios_csv(self.escribir_csv(self.CSV)))
        # Comparar eventos completos prueba precio, fecha, símbolo y orden a la vez.
        self.assertEqual(eventos, [evento_en(0, 67.0), evento_en(1, 69.5),
                                   evento_en(2, 91.0), evento_en(3, 1943.0)])

    def test_omite_filas_invalidas(self):
        csv_malo = (
            "datetime,close\n"
            "2021-01-01 00:00:00+00:00,13\n"        # válida
            ",50\n"                                   # sin fecha
            "2021-01-01 00:01:00+00:00,NaN\n"        # precio NaN
            "2021-01-01 00:02:00+00:00,abc\n"        # precio no numérico
            "2021-01-01 00:03:00+00:00,\n"           # precio vacío
            "2021-01-01 00:04:00+00:00,0\n"          # precio cero
            "2021-01-01 00:05:00+00:00,-3\n"         # precio negativo
            "2021-01-01 00:06:00+00:00,777.7\n"      # válida
        )
        eventos = list(generar_precios_csv(self.escribir_csv(csv_malo)))
        self.assertEqual(eventos, [evento_en(0, 13.0), evento_en(6, 777.7)])

    def test_filtra_por_rango_de_fechas(self):
        eventos = list(generar_precios_csv(
            self.escribir_csv(self.CSV),
            desde=utc(2021, 1, 1, 0, 1), hasta=utc(2021, 1, 1, 0, 2)))
        self.assertEqual(eventos, [evento_en(1, 69.5), evento_en(2, 91.0)])


# ---------------------------------------------------------------------------
# filtrar_rango
# ---------------------------------------------------------------------------

class TestFiltrarRango(unittest.TestCase):
    def setUp(self):
        self.eventos = [evento_en(m, 67 + m) for m in range(6)]  # minutos 0 a 5

    def minutos(self, flujo):
        return [e.timestamp.minute for e in flujo]

    def test_respeta_los_limites_e_incluye_los_extremos(self):
        todo = filtrar_rango(iter(self.eventos))
        solo_desde = filtrar_rango(iter(self.eventos), desde=utc(2021, 1, 1, 0, 3))
        solo_hasta = filtrar_rango(iter(self.eventos), hasta=utc(2021, 1, 1, 0, 2))
        ambos = filtrar_rango(iter(self.eventos),
                              desde=utc(2021, 1, 1, 0, 1), hasta=utc(2021, 1, 1, 0, 3))
        fuera = filtrar_rango(iter(self.eventos), desde=utc(2030, 1, 1))

        self.assertEqual(self.minutos(todo), [0, 1, 2, 3, 4, 5])
        self.assertEqual(self.minutos(solo_desde), [3, 4, 5])
        self.assertEqual(self.minutos(solo_hasta), [0, 1, 2])
        self.assertEqual(self.minutos(ambos), [1, 2, 3])
        self.assertEqual(self.minutos(fuera), [])

    def test_deja_de_leer_al_pasar_hasta(self):
        consumidos = []

        def con_registro():
            for evento in self.eventos:
                consumidos.append(evento.timestamp.minute)
                yield evento

        list(filtrar_rango(con_registro(), hasta=utc(2021, 1, 1, 0, 1)))
        # Leyó el minuto 2 solo para darse cuenta de que ya se pasó; no siguió.
        self.assertEqual(consumidos, [0, 1, 2])


# ---------------------------------------------------------------------------
# Simulador
# ---------------------------------------------------------------------------

class TestGenerarPreciosBtc(unittest.TestCase):
    def tomar(self, n, **kwargs):
        return list(islice(generar_precios_btc(**kwargs), n))

    def test_primer_evento_usa_precio_inicial_utc_e_intervalo(self):
        inicio = utc(2021, 1, 1)
        eventos = self.tomar(4, precio_inicial=777.0, inicio=inicio, intervalo=67, semilla=1)
        self.assertEqual(eventos[0].precio, 777.0)
        self.assertEqual(eventos[0].simbolo, "BTC")
        self.assertEqual([e.timestamp for e in eventos],
                         [inicio + timedelta(seconds=67 * n) for n in range(4)])
        self.assertEqual(self.tomar(1)[0].timestamp.utcoffset(), timedelta(0))

    def test_la_semilla_hace_reproducible_la_secuencia(self):
        a = [e.precio for e in self.tomar(100, semilla=91)]
        b = [e.precio for e in self.tomar(100, semilla=91)]
        c = [e.precio for e in self.tomar(100, semilla=69)]
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_flujo_infinito_y_precio_nunca_baja_de_1(self):
        eventos = self.tomar(1943, precio_inicial=1.3, volatilidad=0.5, semilla=13)
        self.assertEqual(len(eventos), 1943)
        self.assertTrue(all(e.precio >= 1.0 for e in eventos))

    def test_sin_volatilidad_no_hay_cambios_y_los_picos_los_agrandan(self):
        quieto = self.tomar(50, precio_inicial=67.0, volatilidad=0.0, semilla=1)
        self.assertTrue(all(e.precio == 67.0 for e in quieto))

        def mayor_cambio(prob_pico):
            precios = [e.precio for e in self.tomar(
                300, volatilidad=0.001, prob_pico=prob_pico, factor_pico=10, semilla=13)]
            return max(abs(b - a) / a for a, b in zip(precios, precios[1:]))

        self.assertGreater(mayor_cambio(1.0), 5 * mayor_cambio(0.0))


# ---------------------------------------------------------------------------
# con_pausa
# ---------------------------------------------------------------------------

class TestConPausa(unittest.TestCase):
    def test_entrega_los_mismos_eventos_y_espera_tras_cada_uno(self):
        eventos = [evento_en(m) for m in range(13)]
        with patch("src.streams.time.sleep") as falso_sleep:
            flujo = con_pausa(iter(eventos), 0.67)
            falso_sleep.assert_not_called()          # es perezoso
            resultado = list(flujo)
        self.assertEqual(resultado, eventos)
        self.assertEqual(falso_sleep.call_count, 13)
        falso_sleep.assert_called_with(0.67)


if __name__ == "__main__":
    unittest.main()