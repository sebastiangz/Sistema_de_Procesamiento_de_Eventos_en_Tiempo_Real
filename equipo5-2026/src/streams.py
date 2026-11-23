"""Flujo de precios de Bitcoin.

Ideas que se usan en este módulo:
    * Datos inmutables: el evento es una namedtuple, no se modifica.
    * Funciones puras: reciben datos y devuelven datos, sin cambiar nada afuera.
    * Flujos perezosos: map, filter y generadores procesan un evento a la vez,
      sin cargar todo el archivo en memoria.
    * Composición: el flujo final se arma conectando funciones pequeñas.
    * Efectos secundarios aislados: la lectura del archivo y la pausa
      (sleep) están cada una en su propia función.

Hay dos fuentes de eventos:
    * generar_precios_csv: reproduce el dataset histórico de Kaggle.
    * generar_precios_btc: simula precios con picos de volatilidad.
"""

import csv
import random
import time
from collections import namedtuple
from datetime import datetime, timedelta, timezone
from functools import partial
from itertools import accumulate, count, dropwhile, takewhile

# Un evento es una tupla inmutable: (cuándo, qué activo, a qué precio).
Evento = namedtuple("Evento", ["timestamp", "simbolo", "precio"])


# ---------------------------------------------------------------------------
# Funciones puras
# ---------------------------------------------------------------------------

def formatear(evento):
    """Convierte un evento en texto para mostrarlo.

    Args:
        evento: Un Evento.

    Returns:
        Texto con la forma "[2017-08-17 04:00:00] Precio BTC: 4,261.48".
    """
    momento = evento.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return f"[{momento}] Precio {evento.simbolo}: {evento.precio:,.2f}"


def fila_a_evento(simbolo, fila):
    """Convierte una fila del CSV en un Evento.

    Args:
        simbolo: Símbolo del activo (por ejemplo, "BTC").
        fila: Diccionario con las columnas del CSV.

    Returns:
        Un Evento, o None si la fila tiene datos que no se pueden leer.
    """
    try:
        return Evento(
            timestamp=datetime.fromisoformat(fila["datetime"]),
            simbolo=simbolo,
            precio=round(float(fila["close"]), 2),
        )
    except (ValueError, KeyError, TypeError):
        return None


def es_valido(evento):
    """Indica si un evento sirve (existe y tiene precio positivo).

    Args:
        evento: Un Evento o None.

    Returns:
        True si el evento es utilizable. Un precio NaN da False.
    """
    return evento is not None and evento.precio > 0


# ---------------------------------------------------------------------------
# Fuente 1: dataset histórico (CSV de Kaggle)
# ---------------------------------------------------------------------------

def leer_filas(ruta):
    """Lee el CSV fila por fila (único lugar donde se toca el archivo).

    Args:
        ruta: Ruta del archivo CSV.

    Yields:
        Un diccionario por cada fila, con los encabezados como llaves.
    """
    with open(ruta, newline="", encoding="utf-8-sig") as archivo:
        yield from csv.DictReader(archivo)


def filtrar_rango(eventos, desde=None, hasta=None):
    """Se queda solo con los eventos entre dos fechas.

    Supone que los eventos vienen en orden cronológico (así viene el
    dataset), por eso se puede dejar de leer al pasar `hasta`.

    Args:
        eventos: Flujo de eventos ordenado por fecha.
        desde: Primera fecha a incluir (datetime con zona horaria) o None.
        hasta: Última fecha a incluir (datetime con zona horaria) o None.

    Returns:
        Un flujo con los eventos dentro del rango.
    """
    desde_inicio = dropwhile(lambda e: desde is not None and e.timestamp < desde, eventos)
    return takewhile(lambda e: hasta is None or e.timestamp <= hasta, desde_inicio)


def generar_precios_csv(ruta, desde=None, hasta=None, simbolo="BTC"):
    """Arma el flujo de eventos a partir del dataset histórico.

    El flujo se construye componiendo funciones:
    filas -> eventos -> eventos válidos -> eventos dentro del rango.

    Args:
        ruta: Ruta del CSV (usa las columnas "datetime" y "close").
        desde: Primera fecha a incluir (datetime con zona horaria) o None.
        hasta: Última fecha a incluir (datetime con zona horaria) o None.
        simbolo: Símbolo del activo.

    Returns:
        Un flujo (iterador) de Evento.
    """
    eventos = map(partial(fila_a_evento, simbolo), leer_filas(ruta))
    validos = filter(es_valido, eventos)
    return filtrar_rango(validos, desde, hasta)


# ---------------------------------------------------------------------------
# Fuente 2: simulador
# ---------------------------------------------------------------------------

def generar_precios_btc(precio_inicial=67_000.0, volatilidad=0.0005,
                        prob_pico=0.02, factor_pico=8.0, intervalo=1.0,
                        semilla=None, inicio=None, simbolo="BTC"):
    """Simula un flujo infinito de precios con picos de volatilidad.

    Cada precio se calcula a partir del anterior con accumulate (un
    "fold" que va guardando los resultados parciales), sin variables que
    cambien dentro de un ciclo.

    Args:
        precio_inicial: Precio del primer evento, en USD.
        volatilidad: Desviación estándar del cambio normal por evento (0.0005 equivale a 0.05 %).
        prob_pico: Probabilidad (entre 0 y 1) de que un evento sea un pico.
        factor_pico: Cuántas veces mayor es el cambio durante un pico.
        intervalo: Segundos que separan un evento del siguiente.
        semilla: Semilla aleatoria, para obtener siempre la misma secuencia.
        inicio: Fecha del primer evento (datetime con zona horaria). Si es
        None se usa la hora actual en UTC.
        simbolo: Símbolo del activo.

    Returns:
        Un flujo (iterador) infinito de Evento. Para tomar solo algunos,
        usar itertools.islice.
    """
    azar = random.Random(semilla)
    inicio = inicio or datetime.now(timezone.utc)

    def cambio_porcentual(_):
        sigma = volatilidad * factor_pico if azar.random() < prob_pico else volatilidad
        return azar.gauss(0, sigma)

    def siguiente_precio(precio, cambio):
        return max(1.0, precio * (1 + cambio))  # el precio nunca baja de 1 USD

    cambios = map(cambio_porcentual, count())
    precios = accumulate(cambios, siguiente_precio, initial=precio_inicial)
    tiempos = (inicio + timedelta(seconds=n * intervalo) for n in count())

    return (Evento(t, simbolo, round(p, 2)) for t, p in zip(tiempos, precios))


# ---------------------------------------------------------------------------
# Efecto secundario aislado: la pausa entre eventos
# ---------------------------------------------------------------------------

def con_pausa(eventos, segundos):
    """Hace que el flujo avance a una velocidad (simula tiempo real).

    Args:
        eventos: Cualquier flujo de eventos.
        segundos: Segundos de espera después de cada evento.

    Yields:
        Los mismos eventos, uno cada `segundos` segundos.
    """
    for evento in eventos:
        yield evento
        time.sleep(segundos)


if __name__ == "__main__":
    from itertools import islice

    # Demostración: 5 eventos simulados, sin pausa.
    for linea in map(formatear, islice(generar_precios_btc(semilla=42), 5)):
        print(linea)
