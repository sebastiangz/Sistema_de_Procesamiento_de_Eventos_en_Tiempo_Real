from datetime import datetime, timedelta, timezone
from itertools import islice

import pytest

from src.reglas import (
    Alerta,
    REGLAS_POR_DEFECTO,
    crear_alerta,
    duracion,
    evaluar,
    formatear_alerta,
    generar_alertas,
    regla_salto,
    regla_variacion,
    regla_volatilidad,
    retornos,
    variacion_porcentual,
)
from src.streams import Evento, generar_precios_btc

T0 = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)


def hacer_ventana(precios, simbolo="BTC"):
    """Arma una ventana con un evento por segundo."""
    return tuple(
        Evento(T0 + timedelta(seconds=i), simbolo, p) for i, p in enumerate(precios)
    )



# Funciones auxiliares


def test_duracion():
    assert duracion(hacer_ventana([67, 69, 96, 99])) == 3.0
    assert duracion(hacer_ventana([777])) == 0.0
    assert duracion(()) == 0.0


def test_variacion_porcentual_sube_y_baja():
    assert variacion_porcentual(96, 99) == pytest.approx(3.125)
    assert variacion_porcentual(99, 96) == pytest.approx(-3.030303)


def test_variacion_porcentual_precio_inicial_invalido():
    assert variacion_porcentual(0, 777) == 0.0
    assert variacion_porcentual(-1, 777) == 0.0


def test_retornos():
    assert retornos(hacer_ventana([1, 0])) == pytest.approx((-100.0,))
    assert retornos(hacer_ventana([67])) == ()


def test_crear_alerta_usa_ultimo_evento():
    ventana = hacer_ventana([96, 99])
    alerta = crear_alerta(ventana, "PRUEBA", 3.12345)
    assert alerta == Alerta(ventana[-1].timestamp, "BTC", "PRUEBA", 3.12, 1.0)



# Regla de variación


def test_variacion_alerta_cuando_sube():
    alerta = regla_variacion(2.0)(hacer_ventana([67, 68, 69]))
    assert alerta is not None
    assert alerta.tipo == "VARIACION"
    assert alerta.valor == 2.99


def test_variacion_alerta_cuando_baja():
    alerta = regla_variacion(2.0)(hacer_ventana([99, 98, 96]))
    assert alerta is not None
    assert alerta.valor == -3.03


def test_variacion_casos_limite():
    assert regla_variacion(2.0)(hacer_ventana([100, 100.5, 101])) is None  # bajo el umbral
    assert regla_variacion(2.0)(hacer_ventana([777])) is None              # ventana corta
    assert regla_variacion(2.0)(hacer_ventana([100, 102])) is not None     # umbral exacto



# Regla de salto


def test_salto_alerta_con_cambio_brusco_al_final():
    alerta = regla_salto(1.0)(hacer_ventana([67, 67, 67, 69]))
    assert alerta is not None
    assert alerta.tipo == "SALTO"
    assert alerta.valor == 2.99


def test_salto_ignora_cambios_viejos_y_ventana_corta():
    assert regla_salto(1.0)(hacer_ventana([100, 120, 120.1])) is None
    assert regla_salto(1.0)(hacer_ventana([69])) is None



# Regla de volatilidad


def test_volatilidad_alerta_con_precios_inestables():
    alerta = regla_volatilidad(1.0)(hacer_ventana([67, 96, 69, 99, 67]))
    assert alerta is not None
    assert alerta.tipo == "VOLATILIDAD"


def test_volatilidad_no_alerta_si_es_estable_o_hay_pocos_datos():
    assert regla_volatilidad(1.0)(hacer_ventana([100, 100.1, 100.2, 100.3])) is None
    assert regla_volatilidad(0.1)(hacer_ventana([1, 777])) is None


# Composición


def test_evaluar_devuelve_solo_alertas_activadas():
    reglas = (regla_variacion(2.0), regla_salto(10.0))
    alertas = evaluar(reglas, hacer_ventana([96, 97, 99]))
    assert tuple(a.tipo for a in alertas) == ("VARIACION",)


def test_evaluar_sin_alertas_y_sin_modificar_la_ventana():
    ventana = hacer_ventana([777, 777, 777])
    copia = tuple(ventana)
    assert evaluar(REGLAS_POR_DEFECTO, ventana) == ()
    assert ventana == copia


def test_generar_alertas_aplana_varias_ventanas():
    ventanas = [
        hacer_ventana([69, 69]),        
        hacer_ventana([67, 69]),        
        hacer_ventana([96, 96.1]),      
    ]
    reglas = (regla_variacion(2.0), regla_salto(1.0))
    alertas = list(generar_alertas(ventanas, reglas))
    assert [a.tipo for a in alertas] == ["VARIACION", "SALTO"]


def test_generar_alertas_es_perezoso_con_flujo_infinito():
    def ventanas():
        while True:
            yield hacer_ventana([99, 777])

    primeras = list(islice(generar_alertas(ventanas(), (regla_salto(1.0),)), 3))
    assert len(primeras) == 3


def test_integracion_con_simulador():
    precios = generar_precios_btc(semilla=1, inicio=T0)
    ventanas = (tuple(islice(precios, 10)) for _ in range(20))
    alertas = list(generar_alertas(ventanas, REGLAS_POR_DEFECTO))
    assert all(isinstance(a, Alerta) for a in alertas)


# Formato


def test_formatear_alerta_positiva_y_negativa():
    positiva = Alerta(T0, "BTC", "VARIACION", 69.0, 99.0)
    negativa = Alerta(T0, "BTC", "SALTO", -67.0, 96.0)
    assert formatear_alerta(positiva) == (
        "!!! ALERTA [VARIACION] BTC: variación de +69.00% en 99 s !!!"
    )
    assert "-67.00%" in formatear_alerta(negativa)# Archivo inicial
