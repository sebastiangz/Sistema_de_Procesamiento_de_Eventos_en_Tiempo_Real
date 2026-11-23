"""Punto de entrada: conecta streams, state y reglas."""

from datetime import datetime, timezone
from itertools import islice

from src.reglas import REGLAS_POR_DEFECTO, formatear_alerta
from src.state import formatear_estado, generar_estados
from src.streams import (
    con_pausa,
    formatear,
    generar_precios_btc,
    generar_precios_csv,
)

USAR_DATASET = False  # True: precios históricos del CSV; False: simulador
RUTA_CSV = "data/processed_trading_data2.csv"
EVENTOS = 60
PAUSA = 0.2
VENTANA = 10


def crear_eventos():
    """Devuelve el flujo de eventos: dataset histórico o simulador."""
    if USAR_DATASET:
        # Desde el 17 de diciembre de 2017
        desde = datetime(2017, 12, 17, 12, 0, tzinfo=timezone.utc)
        eventos = generar_precios_csv(RUTA_CSV, desde=desde)
    else:
        eventos = generar_precios_btc(volatilidad=0.001, semilla=42)
    return islice(eventos, EVENTOS)


def main():
    """Procesa los eventos y muestra eventos, alertas y resúmenes."""
    eventos = con_pausa(crear_eventos(), PAUSA)
    estados = generar_estados(eventos, REGLAS_POR_DEFECTO, VENTANA)
    for estado in estados:
        print(formatear(estado.ventana[-1]))
        for alerta in estado.alertas_nuevas:
            print("   ", formatear_alerta(alerta))
        if estado.total_eventos % 20 == 0:
            print("--", formatear_estado(estado))


"""Punto de entrada: conecta streams, state y reglas."""

from datetime import datetime, timezone
from itertools import islice

from src.operadores import (
    filtrar_por_cambio,
    promedio_precios,
    variaciones_consecutivas,
)
from src.reglas import REGLAS_POR_DEFECTO, formatear_alerta
from src.state import formatear_estado, generar_estados
from src.streams import (
    con_pausa,
    formatear,
    generar_precios_btc,
    generar_precios_csv,
)

USAR_DATASET = False  # True: precios históricos del CSV; False: simulador
RUTA_CSV = "data/processed_trading_data2.csv"
EVENTOS = 60  # cuántos eventos procesar
PAUSA = 0.2  # segundos entre eventos
VENTANA = 10  # eventos que recuerda el estado
UMBRAL_SALTO = 0.2  # % de cambio entre dos eventos para contarlo como salto grande


def crear_eventos():
    """Devuelve el flujo de eventos: dataset histórico o simulador."""
    if USAR_DATASET:
        # Desde el 5 de febrero de 2018, un día de fuerte caída del Bitcoin
        desde = datetime(2018, 2, 5, 10, 0, tzinfo=timezone.utc)
        eventos = generar_precios_csv(RUTA_CSV, desde=desde)
    else:
        eventos = generar_precios_btc(volatilidad=0.002, semilla=42)
    return islice(eventos, EVENTOS)


def resumen_operadores(estado):
    """Texto con la media móvil y los saltos grandes de la ventana."""
    media = promedio_precios(estado.ventana)  # reduce
    cambios = variaciones_consecutivas(estado.ventana)  # map
    saltos = tuple(filtrar_por_cambio(cambios, UMBRAL_SALTO))  # filter
    return f"Media: {media:,.2f} | Saltos >= {UMBRAL_SALTO}%: {len(saltos)}"


def main():
    """Procesa los eventos y muestra eventos, alertas y resúmenes."""
    eventos = con_pausa(crear_eventos(), PAUSA)
    estados = generar_estados(eventos, REGLAS_POR_DEFECTO, VENTANA)
    for estado in estados:
        print(formatear(estado.ventana[-1]))
        for alerta in estado.alertas_nuevas:
            print("   ", formatear_alerta(alerta))
        if estado.total_eventos % 20 == 0:
            print("--", formatear_estado(estado), "|", resumen_operadores(estado))


if __name__ == "__main__":
    main()
