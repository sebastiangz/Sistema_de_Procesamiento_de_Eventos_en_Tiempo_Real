"""Pruebas de src/operadores.py.
Ejecutación:
    python -m pytest tests/
"""
# pylint: disable=missing-function-docstring

from collections import namedtuple
import pytest

from src.operadores import (
    calcular_cambio,
    variacion_entre,
    variacion_en_ventana,
    pares_consecutivos,
    ventanas,
    variaciones_consecutivas,
    variaciones_en_ventanas,
    filtrar_por_cambio,
    promedio_precios,
)

# Evento de prueba
Evento = namedtuple(
    "Evento",
    ["timestamp", "simbolo", "precio"]
)

eventos = [
    Evento("10:00", "BTC", 100),
    Evento("10:01", "BTC", 110),
    Evento("10:02", "BTC", 105),
    Evento("10:03", "BTC", 120),
]


# 1. PRUEBAS DE CALCULAR CAMBIO

def test_calcular_cambio():
    assert calcular_cambio(100, 110) == 10
    assert calcular_cambio(100, 90) == -10
    assert calcular_cambio(100, 100) == 0


def test_calcular_cambio_cero():
    with pytest.raises(ValueError):
        calcular_cambio(0, 100)


# 2. PRUEBAS DE VARIACION ENTRE EVENTOS

def test_variacion_entre():
    resultado = variacion_entre(eventos[0], eventos[1])

    assert resultado.precio_anterior == 100
    assert resultado.precio == 110
    assert resultado.cambio == 10
    assert resultado.simbolo == "BTC"


def test_variacion_en_ventana():
    resultado = variacion_en_ventana(eventos)

    assert resultado.precio_anterior == 100
    assert resultado.precio == 120
    assert resultado.cambio == 20


# 3. PRUEBAS DE VENTANAS

def test_pares_consecutivos():
    resultado = list(pares_consecutivos(eventos))

    assert resultado == [
        (eventos[0], eventos[1]),
        (eventos[1], eventos[2]),
        (eventos[2], eventos[3]),
    ]


def test_ventanas():
    resultado = list(ventanas(eventos, 2))

    assert len(resultado) == 3
    assert resultado[0] == (eventos[0], eventos[1])
    assert resultado[1] == (eventos[1], eventos[2])
    assert resultado[2] == (eventos[2], eventos[3])


def test_ventanas_tamano_invalido():
    with pytest.raises(ValueError):
        ventanas(eventos, 0)


# 4. PRUEBAS DE MAP

def test_variaciones_consecutivas():
    resultado = list(variaciones_consecutivas(eventos))

    assert len(resultado) == 3
    assert resultado[0].cambio == 10
    assert resultado[1].cambio == pytest.approx(-4.5454545)
    assert resultado[2].cambio == pytest.approx(14.285714)


def test_variaciones_en_ventanas():
    resultado = list(variaciones_en_ventanas(eventos, 2))

    assert len(resultado) == 3
    assert resultado[0].cambio == 10
    assert resultado[1].cambio == pytest.approx(-4.5454545)
    assert resultado[2].cambio == pytest.approx(14.285714)


# 5. PRUEBAS DE FILTER

def test_filtrar_por_cambio():
    variaciones = list(variaciones_consecutivas(eventos))

    resultado = list(filtrar_por_cambio(variaciones, 10))

    assert len(resultado) == 2
    assert resultado[0].cambio == 10
    assert resultado[1].cambio == pytest.approx(14.285714)


# 6. PRUEBAS DE REDUCE

def test_promedio_precios():
    resultado = promedio_precios(eventos)

    assert resultado == 108.75


def test_promedio_sin_eventos():
    with pytest.raises(ValueError):
        promedio_precios([])


# Ejecutar todas las pruebas
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
# Archivo inicial
