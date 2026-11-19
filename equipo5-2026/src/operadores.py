"""Operadores funcionales para transformar el flujo de precios de Bitcoin.

Recibe el flujo de `Evento` que produce `streams.py` y lo transforma con
funciones puras y perezosas (map, filter, reduce y ventanas).

Operadores:
    * Cambio porcentual: `calcular_cambio`, `variacion_entre`.
    * map: `variaciones_consecutivas` (cada evento contra el anterior) y
      `variaciones_en_ventanas` (el cambio dentro de una ventana de eventos).
    * filter: `filtrar_por_cambio` (conserva los cambios grandes).
    * reduce: `promedio_precios` (promedio de los precios de un grupo).
    * ventanas: `pares_consecutivos` y `ventanas` (ventana deslizante).

Ejemplo de uso con el flujo del simulador:
    flujo = generar_precios_btc(semilla=42)
    cambios = variaciones_en_ventanas(flujo, tamano=5)
    grandes = filtrar_por_cambio(cambios, umbral=0.1)

Demostración:
    python -m src.operadores
"""

from collections import namedtuple
from functools import reduce
from itertools import islice, starmap, tee

# Resultado de comparar dos precios: el cambio entre `precio_anterior` y
# `precio` (en porcentaje), con la fecha y el símbolo del evento más reciente.
Variacion = namedtuple(
    "Variacion",
    ["timestamp", "simbolo", "precio_anterior", "precio", "cambio"],
)


# ---------------------------------------------------------------------------
# Cálculo del cambio (funciones puras)
# ---------------------------------------------------------------------------

def calcular_cambio(precio_anterior, precio):
    """Calcula el cambio porcentual entre dos precios.

    Args:
        precio_anterior: Precio inicial. No puede ser 0.
        precio: Precio final.

    Returns:
        El cambio en porcentaje: positivo si el precio subió y negativo
        si bajó (de 100 a 103 devuelve 3.0).

    Raises:
        ValueError: Si `precio_anterior` es 0.
    """
    if precio_anterior == 0:
        raise ValueError("precio_anterior no puede ser 0")
    return (precio - precio_anterior) / precio_anterior * 100


def variacion_entre(inicial, final):
    """Compara dos eventos y devuelve la variación entre ellos.

    Args:
        inicial: Evento de partida.
        final: Evento de llegada (el más reciente).

    Returns:
        Una Variacion con la fecha y el símbolo de `final`.
    """
    return Variacion(
        timestamp=final.timestamp,
        simbolo=final.simbolo,
        precio_anterior=inicial.precio,
        precio=final.precio,
        cambio=calcular_cambio(inicial.precio, final.precio),
    )


def variacion_en_ventana(ventana):
    """Calcula la variación de una ventana: del primer al último evento.

    Args:
        ventana: Tupla de eventos en orden cronológico.

    Returns:
        Una Variacion entre el primer y el último evento de la ventana.
    """
    return variacion_entre(ventana[0], ventana[-1])


# ---------------------------------------------------------------------------
# Ventanas
# ---------------------------------------------------------------------------

def pares_consecutivos(eventos):
    """Empareja cada evento con el que viene justo después.

    Args:
        eventos: Flujo de eventos (puede ser infinito).

    Returns:
        Un flujo de pares (evento, siguiente). De [a, b, c] devuelve
        (a, b) y (b, c).
    """
    anteriores, siguientes = tee(eventos)
    next(siguientes, None)
    return zip(anteriores, siguientes)


def ventanas(eventos, tamano):
    """Agrupa el flujo en ventanas deslizantes de `tamano` eventos.

    Cada ventana avanza un evento a la vez, así que de [a, b, c, d] con
    tamano 3 salen (a, b, c) y (b, c, d). Se calcula con `tee` e `islice`,
    sin guardar listas completas ni variables que cambien.

    Args:
        eventos: Flujo de eventos (puede ser infinito).
        tamano: Cantidad de eventos de cada ventana (1 o más).

    Returns:
        Un flujo de tuplas con `tamano` eventos consecutivos. Si el flujo
        tiene menos eventos que `tamano`, no produce ventanas.

    Raises:
        ValueError: Si `tamano` es menor que 1.
    """
    if tamano < 1:
        raise ValueError("tamano debe ser 1 o más")
    copias = tee(eventos, tamano)
    desplazadas = (islice(copia, posicion, None) for posicion, copia in enumerate(copias))
    return zip(*desplazadas)


# ---------------------------------------------------------------------------
# Operadores sobre el flujo: map, filter y reduce
# ---------------------------------------------------------------------------

def variaciones_consecutivas(eventos):
    """MAP: calcula el cambio de cada evento respecto al anterior.

    Args:
        eventos: Flujo de eventos en orden cronológico.

    Returns:
        Un flujo de Variacion, una por cada par de eventos consecutivos.
    """
    return starmap(variacion_entre, pares_consecutivos(eventos))


def variaciones_en_ventanas(eventos, tamano):
    """MAP: calcula el cambio dentro de cada ventana deslizante.

    Sirve para medir movimientos que se ven mejor en un tramo largo que
    entre dos eventos seguidos (por ejemplo, el cambio en los últimos 30
    minutos de datos por minuto).

    Nota:
        La ventana cuenta eventos, no tiempo. Si el dataset tiene huecos
        (minutos sin datos), una ventana de 30 eventos puede abarcar más
        de 30 minutos reales; el campo `timestamp` de la Variacion es el
        del último evento de la ventana.

    Args:
        eventos: Flujo de eventos en orden cronológico.
        tamano: Cantidad de eventos de cada ventana (1 o más).

    Returns:
        Un flujo de Variacion, una por cada ventana completa.

    Raises:
        ValueError: Si `tamano` es menor que 1.
    """
    return map(variacion_en_ventana, ventanas(eventos, tamano))


def filtrar_por_cambio(variaciones, umbral):
    """FILTER: conserva las variaciones cuyo cambio es grande.

    Args:
        variaciones: Flujo de Variacion.
        umbral: Cambio mínimo, en porcentaje. Se compara el valor absoluto,
            así que cuentan tanto las subidas como las bajadas, y un cambio
            igual al umbral sí se conserva.

    Returns:
        Un flujo con las variaciones cuyo |cambio| es mayor o igual al umbral.
    """
    return filter(lambda variacion: abs(variacion.cambio) >= umbral, variaciones)


def promedio_precios(eventos):
    """REDUCE: calcula el promedio de los precios de un grupo de eventos.

    Útil junto con `ventanas` para obtener una media móvil:
    `map(promedio_precios, ventanas(flujo, 10))`.

    Args:
        eventos: Eventos del mismo activo (por ejemplo, una ventana).

    Returns:
        El promedio de los precios.

    Raises:
        ValueError: Si no hay eventos.
    """
    eventos = tuple(eventos)
    if not eventos:
        raise ValueError("no hay eventos para promediar")
    suma = reduce(lambda acumulado, evento: acumulado + evento.precio, eventos, 0.0)
    return suma / len(eventos)


if __name__ == "__main__":
    # pylint: disable=import-outside-toplevel
    from src.streams import formatear, generar_precios_btc

    flujo = list(islice(generar_precios_btc(semilla=42, volatilidad=0.001), 40))

    print("Primeros 5 eventos:")
    for evento in islice(flujo, 5):
        print(" ", formatear(evento))

    print("\nCambio de cada evento contra el anterior (primeros 3):")
    for variacion in islice(variaciones_consecutivas(flujo), 3):
        print(f"  {variacion.precio_anterior:,.2f} -> {variacion.precio:,.2f}"
              f"  ({variacion.cambio:+.3f} %)")

    print("\nPrimeras 5 ventanas de 10 eventos con un cambio de 0.2 % o más:")
    cambios = variaciones_en_ventanas(flujo, tamano=10)
    for variacion in islice(filtrar_por_cambio(cambios, umbral=0.2), 5):
        print(f"  {variacion.timestamp:%H:%M:%S}  {variacion.cambio:+.3f} %")

    medias = map(promedio_precios, ventanas(flujo, 10))
    print(f"\nÚltima media móvil de 10 eventos: {list(medias)[-1]:,.2f}")
