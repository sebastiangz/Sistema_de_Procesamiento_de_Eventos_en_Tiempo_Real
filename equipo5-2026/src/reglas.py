from collections import namedtuple
from functools import partial
from itertools import chain
from statistics import pstdev


Alerta = namedtuple("Alerta", ["timestamp", "simbolo", "tipo", "valor", "segundos"])


# Funciones 

def duracion(ventana):
    """Segundos que abarca la ventana (del primer al último evento).

    Args:
        ventana: Secuencia de Evento ordenada por fecha.

    Returns:
        Segundos como float. 0.0 si la ventana tiene menos de 2 eventos.
    """
    if len(ventana) < 2:
        return 0.0
    return (ventana[-1].timestamp - ventana[0].timestamp).total_seconds()


def variacion_porcentual(precio_inicial, precio_final):
    """Calcula el cambio porcentual entre dos precios.

    Args:
        precio_inicial: Precio de referencia (mayor que 0).
        precio_final: Precio nuevo.

    Returns:
        El cambio en porcentaje (puede ser negativo). 0.0 si el precio
        inicial no es mayor que 0.
    """
    if precio_inicial <= 0:
        return 0.0
    return (precio_final - precio_inicial) / precio_inicial * 100


def retornos(ventana):
    """Cambios porcentuales entre eventos consecutivos de la ventana.

    Args:
        ventana: Secuencia de Evento.

    Returns:
        Tupla de floats (un elemento menos que la ventana).
    """
    return tuple(
        variacion_porcentual(a.precio, b.precio)
        for a, b in zip(ventana, ventana[1:])
    )


def crear_alerta(ventana, tipo, valor):
    """Construye una Alerta usando el último evento de la ventana.

    Args:
        ventana: Secuencia de Evento (no vacía).
        tipo: Nombre de la regla que se activó.
        valor: Número que disparó la alerta (en %).

    Returns:
        Una Alerta.
    """
    ultimo = ventana[-1]
    return Alerta(
        timestamp=ultimo.timestamp,
        simbolo=ultimo.simbolo,
        tipo=tipo,
        valor=round(valor, 2),
        segundos=duracion(ventana),
    )



# Reglas 


def _regla_variacion(umbral, ventana):
    """Se activa si el precio cambió más de `umbral` % en toda la ventana."""
    if len(ventana) < 2:
        return None
    cambio = variacion_porcentual(ventana[0].precio, ventana[-1].precio)
    return crear_alerta(ventana, "VARIACION", cambio) if abs(cambio) >= umbral else None


def _regla_salto(umbral, ventana):
    """Se activa si el último evento saltó más de `umbral` % respecto al anterior."""
    if len(ventana) < 2:
        return None
    cambio = variacion_porcentual(ventana[-2].precio, ventana[-1].precio)
    return crear_alerta(ventana, "SALTO", cambio) if abs(cambio) >= umbral else None


def _regla_volatilidad(umbral, ventana):
    """Se activa si la desviación estándar de los retornos supera `umbral` %."""
    r = retornos(ventana)
    if len(r) < 2:
        return None
    sigma = pstdev(r)
    return crear_alerta(ventana, "VOLATILIDAD", sigma) if sigma >= umbral else None


def regla_variacion(umbral=2.0):
    """Crea la regla de variación total en la ventana.

    Args:
        umbral: Porcentaje mínimo (en valor absoluto) para alertar.

    Returns:
        Una regla: ventana -> Alerta | None.
    """
    return partial(_regla_variacion, umbral)


def regla_salto(umbral=1.0):
    """Crea la regla de salto brusco entre dos eventos seguidos.

    Args:
        umbral: Porcentaje mínimo (en valor absoluto) para alertar.

    Returns:
        Una regla: ventana -> Alerta | None.
    """
    return partial(_regla_salto, umbral)


def regla_volatilidad(umbral=0.1):
    """Crea la regla de volatilidad (desviación estándar de retornos).

    Args:
        umbral: Desviación estándar mínima, en %, para alertar.

    Returns:
        Una regla: ventana -> Alerta | None.
    """
    return partial(_regla_volatilidad, umbral)



# Composición


def evaluar(reglas, ventana):
    """Aplica todas las reglas a una ventana y se queda con las alertas.

    Args:
        reglas: Secuencia de reglas.
        ventana: Secuencia de Evento.

    Returns:
        Tupla con las alertas generadas (puede estar vacía).
    """
    resultados = map(lambda regla: regla(ventana), reglas)
    return tuple(filter(lambda a: a is not None, resultados))


def generar_alertas(ventanas, reglas):
    """Convierte un flujo de ventanas en un flujo de alertas.

    Es perezoso: sirve igual con flujos infinitos (el simulador).

    Args:
        ventanas: Iterable de ventanas (cada una, una secuencia de Evento).
        reglas: Secuencia de reglas.

    Returns:
        Un iterador de Alerta.
    """
    return chain.from_iterable(map(partial(evaluar, reglas), ventanas))


def formatear_alerta(alerta):
    """Convierte una alerta en texto para mostrarla.

    Args:
        alerta: Una Alerta.

    Returns:
        Texto como "!!! ALERTA [VARIACION]: variación de 2.4% en 10 s !!!".
    """
    return (f"!!! ALERTA [{alerta.tipo}] {alerta.simbolo}: "
            f"variación de {alerta.valor:+.2f}% en {alerta.segundos:.0f} s !!!")


REGLAS_POR_DEFECTO = (regla_variacion(2.0), regla_salto(1.0), regla_volatilidad(0.1))


if __name__ == "__main__":
    from datetime import datetime, timezone
    from streams import Evento

    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    precios = (67000, 67010, 67005, 68500)
    ventana = tuple(
        Evento(t0.replace(second=i), "BTC", p) for i, p in enumerate(precios)
    )
    for alerta in evaluar(REGLAS_POR_DEFECTO, ventana):
        print(formatear_alerta(alerta))
