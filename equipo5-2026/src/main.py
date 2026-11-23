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


if __name__ == "__main__":
    main()