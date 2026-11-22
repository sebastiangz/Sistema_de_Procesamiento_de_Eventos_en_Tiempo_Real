"""Estado del sistema entre un evento y el siguiente.

El sistema necesita recordar cosas de un evento al siguiente: los últimos
precios, cuántos eventos van, el precio máximo y mínimo, y cuántas alertas
se han emitido. En lugar de guardarlo en variables globales que cambian,
aquí el estado es un dato inmutable (`Estado`) y cada evento produce
un estado nuevo con una función pura. Así el estado anterior nunca
se modifica y es fácil de probar.

Idea principal: el flujo de estados es un "fold con resultados parciales".
`accumulate` toma el estado inicial y le va aplicando cada evento:

    estado0 --evento1--> estado1 --evento2--> estado2 --> ...

Funciones principales:
    * `crear_estado`: estado inicial, sin eventos.
    * `actualizar_estado`: agrega un evento (ventana, contador, máx y mín).
    * `registrar_alertas`: anota las alertas que se generaron.
    * `procesar_evento`: un paso completo (actualiza y evalúa las reglas).
    * `generar_estados`: convierte un flujo de eventos en un flujo de estados.
    * `alertas_de`: saca las alertas de un flujo de estados.
    * `formatear_estado`: convierte el estado en un resumen de texto.

Ejemplo de uso con el flujo del simulador (infinito, por eso se toman solo
los primeros 40 eventos):
    flujo = islice(generar_precios_btc(semilla=42), 40)
    estados = generar_estados(flujo, REGLAS_POR_DEFECTO, tamano_ventana=10)
    for alerta in alertas_de(estados):
        print(formatear_alerta(alerta))

Para ver una demostración (desde la raíz del proyecto):
    python -m src.state
"""

from collections import namedtuple
from functools import partial
from itertools import accumulate, chain, islice
from operator import attrgetter

from src.reglas import evaluar

# Foto del sistema después de procesar un evento.
#   tamano_ventana: cuántos eventos recientes se recuerdan.
#   ventana: tupla con los últimos `tamano_ventana` eventos (el más viejo primero).
#   total_eventos: cuántos eventos se han procesado.
#   precio_maximo, precio_minimo: extremos vistos (-inf e inf si no hay eventos).
#   total_alertas: cuántas alertas se han emitido en total.
#   ultima_alerta: la alerta más reciente (None si todavía no hubo ninguna).
#   alertas_nuevas: alertas generadas por el último evento (tupla, puede ser vacía).
Estado = namedtuple(
    "Estado",
    [
        "tamano_ventana",
        "ventana",
        "total_eventos",
        "precio_maximo",
        "precio_minimo",
        "total_alertas",
        "ultima_alerta",
        "alertas_nuevas",
    ],
)


# ---------------------------------------------------------------------------
# Transiciones del estado (funciones puras)
# ---------------------------------------------------------------------------

def crear_estado(tamano_ventana=10):
    """Crea el estado inicial: todavía no se ha procesado ningún evento.

    Args:
        tamano_ventana: Cuántos eventos recientes se recuerdan.

    Returns:
        Un Estado vacío.

    Raises:
        ValueError: Si `tamano_ventana` es menor que 1.
    """
    if tamano_ventana < 1:
        raise ValueError("tamano_ventana debe ser 1 o más")
    return Estado(
        tamano_ventana=tamano_ventana,
        ventana=(),
        total_eventos=0,
        precio_maximo=float("-inf"),
        precio_minimo=float("inf"),
        total_alertas=0,
        ultima_alerta=None,
        alertas_nuevas=(),
    )


def actualizar_estado(estado, evento):
    """Agrega un evento al estado y devuelve un estado nuevo.

    No modifica el estado recibido. La ventana conserva solo los últimos
    `tamano_ventana` eventos, y las alertas nuevas quedan vacías (se
    llenan después con `registrar_alertas`).

    Args:
        estado: Estado actual.
        evento: Evento que acaba de llegar.

    Returns:
        Un Estado nuevo que incluye el evento.
    """
    ventana = (estado.ventana + (evento,))[-estado.tamano_ventana:]
    return estado._replace(
        ventana=ventana,
        total_eventos=estado.total_eventos + 1,
        precio_maximo=max(estado.precio_maximo, evento.precio),
        precio_minimo=min(estado.precio_minimo, evento.precio),
        alertas_nuevas=(),
    )


def ventana_llena(estado):
    """Indica si la ventana ya tiene `tamano_ventana` eventos.

    Args:
        estado: Estado actual.

    Returns:
        True si la ventana está completa.
    """
    return len(estado.ventana) == estado.tamano_ventana


def registrar_alertas(estado, alertas):
    """Anota en el estado las alertas que se acaban de generar.

    Args:
        estado: Estado actual.
        alertas: Tupla de Alerta.

    Returns:
        Un Estado nuevo con el total de alertas actualizado. Si no hay
        alertas, conserva la última alerta anterior.
    """
    return estado._replace(
        total_alertas=estado.total_alertas + len(alertas),
        ultima_alerta=alertas[-1] if alertas else estado.ultima_alerta,
        alertas_nuevas=alertas,
    )


def procesar_evento(reglas, estado, evento):
    """Da un paso completo: agrega el evento y evalúa las reglas.

    Las reglas se evalúan solo cuando la ventana está completa, igual que
    hace `operadores.ventanas`.

    Args:
        reglas: Secuencia de reglas.
        estado: Estado actual.
        evento: Evento que acaba de llegar.

    Returns:
        El Estado después del evento, con sus alertas nuevas.
    """
    con_evento = actualizar_estado(estado, evento)
    alertas = evaluar(reglas, con_evento.ventana) if ventana_llena(con_evento) else ()
    return registrar_alertas(con_evento, alertas)


# ---------------------------------------------------------------------------
# Flujos
# ---------------------------------------------------------------------------

def generar_estados(eventos, reglas, tamano_ventana=10):
    """Convierte un flujo de eventos en un flujo de estados.

    Usa `accumulate`: parte del estado inicial y aplica `procesar_evento`
    con cada evento. Es perezoso, así que sirve con flujos infinitos.

    Args:
        eventos: Flujo de Evento en orden cronológico.
        reglas: Secuencia de reglas.
        tamano_ventana: Cuántos eventos recientes se recuerdan (1 o más).

    Returns:
        Un flujo con un Estado por cada evento (sin incluir el inicial).

    Raises:
        ValueError: Si `tamano_ventana` es menor que 1.
    """
    paso = partial(procesar_evento, reglas)
    estados = accumulate(eventos, paso, initial=crear_estado(tamano_ventana))
    return islice(estados, 1, None)


def alertas_de(estados):
    """Saca las alertas de un flujo de estados, en orden.

    Args:
        estados: Flujo de Estado.

    Returns:
        Un flujo de Alerta.
    """
    return chain.from_iterable(map(attrgetter("alertas_nuevas"), estados))


def formatear_estado(estado):
    """Convierte el estado en un resumen de texto.

    Args:
        estado: Un Estado.

    Returns:
        Texto como "Eventos: 40 | Máx: 67,310.50 | Mín: 66,890.12 | Alertas: 3".
    """
    if estado.total_eventos == 0:
        return "Sin eventos todavía"
    return (f"Eventos: {estado.total_eventos} | "
            f"Máx: {estado.precio_maximo:,.2f} | "
            f"Mín: {estado.precio_minimo:,.2f} | "
            f"Alertas: {estado.total_alertas}")

def _demostracion():
    """Muestra el funcionamiento del estado con el flujo del simulador."""
    # Las importaciones van aquí para que el resto del módulo no dependa
    # de streams.py.
    # pylint: disable=import-outside-toplevel
    from src.reglas import REGLAS_POR_DEFECTO, formatear_alerta
    from src.streams import generar_precios_btc

    flujo = islice(generar_precios_btc(semilla=42, volatilidad=0.001), 40)
    historial = list(generar_estados(flujo, REGLAS_POR_DEFECTO, tamano_ventana=10))

    print("Primeras 5 alertas:")
    for alerta in islice(alertas_de(historial), 5):
        print(" ", formatear_alerta(alerta))

    print("\nResumen final:", formatear_estado(historial[-1]))

if __name__ == "__main__":
    _demostracion()
