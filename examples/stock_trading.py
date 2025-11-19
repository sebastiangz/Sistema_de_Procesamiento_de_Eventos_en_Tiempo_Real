# examples/stock_trading.py
import rx
import pandas as pd
import asyncio
from datetime import datetime
from rx import operators as ops
from rx.scheduler import AsyncIOScheduler   

# Clases del proyecto
from src.streams import Event               
from src.patterns import detect_pattern, high_volatility_pattern
from src.aggregators import moving_average
from src.alerts import console_alerter
from src.dashboard import print_dashboard_line

DATASET_FILE = "TSLA.csv.xls"       
TICKER_SYMBOL = "TSLA"
THROTTLE_INTERVAL = 0.25   # 250 ms entre eventos

# =============================================
# CARGA DEL DATASET 
# =============================================
def load_and_prepare_data(file_path: str, symbol: str):
    print(f"Cargando datos desde: {file_path}")
    try:
        df = pd.read_csv(file_path)
        print(f"✓ Archivo cargado → {len(df)} filas")

        events = []
        for _, row in df.iterrows():
            price = row.get("Close") or row.get("close") or row.get("Adj Close")
            change = row.get("Change_Percent", 0.0)

            event = Event("TICK", {
                "symbol": symbol,
                "price": float(price),
                "change": float(change),
                "date_str": str(row.get("Date", "unknown"))
            })
            events.append(event)

        print(f"✓ {len(events)} eventos listos para el stream")
        return events

    except FileNotFoundError:
        print(f"✗ No se encontró el archivo: {file_path}")
        print("   Coloca TSLA.csv en la carpeta raíz del proyecto (misma altura que la carpeta 'src')")
        return []
    except Exception as e:
        print(f"✗ Error leyendo el CSV: {e}")
        return []

# =============================================
# CARGA Y ARRANQUE
# =============================================
historical_events = load_and_prepare_data(DATASET_FILE, TICKER_SYMBOL)

if not historical_events:
    print("No hay datos → terminando el programa")
    exit()

# Stream principal
source_stream = rx.from_iterable(historical_events).pipe(
    ops.throttle_first(interval=THROTTLE_INTERVAL)
)

dashboard_flow = source_stream.pipe(
    moving_average(window=10),
    ops.map(lambda x: Event("MA_UPDATE", x))
)

alert_flow = source_stream.pipe(
    detect_pattern(high_volatility_pattern, window_size=5, step=1)
)

# =============================================
# SUSCRIPCIONES Y EJECUCIÓN (versión limpia 2025)
# =============================================
print("\n" + "="*60)
print("   STREAMING REACTIVO DE ACCIONES - TSLA   ".center(60))
print("="*60 + "\n")

dashboard_flow.subscribe(on_next=print_dashboard_line)
alert_flow.subscribe(on_next=console_alerter)

print(f"Reproduciendo {len(historical_events)} ticks, uno cada {THROTTLE_INTERVAL}s")
print("Presiona Ctrl+C para detener\n")

async def main():
    scheduler = AsyncIOScheduler()
    source_stream.subscribe(scheduler=scheduler)
    await asyncio.sleep(len(historical_events) * THROTTLE_INTERVAL + 3)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n\nDetenido por el usuario")
print("¡Fin del streaming!")