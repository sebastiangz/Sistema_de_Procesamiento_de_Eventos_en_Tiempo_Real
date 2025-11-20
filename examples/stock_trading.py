#!/usr/bin/env python3
# examples/stock_trading.py
import os
import sys
SCRIPT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import rx
import pandas as pd
import asyncio
from datetime import datetime
from rx import operators as ops
from rx.subject import Subject
from rx.scheduler.eventloop import AsyncIOScheduler

# Clases del proyecto
from src.streams import Event               
from src.patterns import detect_pattern, high_volatility_pattern
from src.aggregators import moving_average
from src.alerts import console_alerter
from src.dashboard import print_dashboard_line

DATASET_FILE = "TSLA.csv.xls"       
TICKER_SYMBOL = "TSLA"
THROTTLE_INTERVAL = 0.25   # 250 ms entre eventos (usar <=0 para desactivar throttling)
MAX_TICKS = int(os.getenv("MAX_TICKS", "200"))  # limit playback for demos

# =============================================
# CARGA DEL DATASET 
# =============================================
def load_and_prepare_data(file_path: str, symbol: str):
    print(f"Cargando datos desde: {file_path}")
    try:
        # If dataset is large, read in chunks and keep only the last MAX_TICKS rows
        if MAX_TICKS and MAX_TICKS > 0:
            from collections import deque
            chunk_size = max(1000, MAX_TICKS)
            dq = deque(maxlen=MAX_TICKS)
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                # extend deque with rows as dicts to keep memory small
                for _, r in chunk.iterrows():
                    dq.append(r.to_dict())
            df = pd.DataFrame(list(dq))
        else:
            df = pd.read_csv(file_path)

        print(f"✓ Archivo cargado → {len(df)} filas")

        # Fallback: if chunked read somehow returned very few rows but file is larger,
        # read tail as a safe fallback (rare case).
        if len(df) <= 1:
            try:
                # cheap heuristic: count file lines
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as fh:
                    total_lines = sum(1 for _ in fh)
                if total_lines > len(df) + 1:
                    print("Nota: la lectura por chunks devolvió pocas filas; realizando fallback con tail() para asegurar suficientes ticks.")
                    df = pd.read_csv(file_path).tail(MAX_TICKS if MAX_TICKS > 0 else None)
                    print(f"✓ Fallback cargado → {len(df)} filas")
            except Exception:
                pass

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
        print("   Se generará un CSV de ejemplo 'TSLA.csv.xls' en la raíz del proyecto.")
        # Generar un CSV de ejemplo sencillo para demo
        from datetime import datetime, timedelta
        import random

        rows = []
        today = datetime.today()
        for i in range(50):
            date = (today - timedelta(days=50 - i)).strftime("%Y-%m-%d")
            price = round(100 + random.uniform(-5, 5) + i * 0.2, 2)
            change = round(random.uniform(-3, 3), 2)
            rows.append({"Date": date, "Close": price, "Change_Percent": change})
        df = pd.DataFrame(rows)
        df.to_csv(file_path, index=False)
        print(f"✓ Archivo de ejemplo creado: {file_path}")
        # now try load again
        try:
            df = pd.read_csv(file_path)
        except Exception:
            return []
    except Exception as e:
        print(f"✗ Error leyendo el CSV: {e}")
        return []

# =============================================
# CARGA Y ARRANQUE
# =============================================
def main():
    historical_events = load_and_prepare_data(DATASET_FILE, TICKER_SYMBOL)

    # Limitar cantidad de ticks para demos/ejecuciones interactivas
    if MAX_TICKS and len(historical_events) > MAX_TICKS:
        print(f"Nota: dataset grande ({len(historical_events)} rows). Se reproducirán solo las primeras {MAX_TICKS} ticks para la demo.")
        historical_events = historical_events[:MAX_TICKS]

    if not historical_events:
        print("No hay datos → terminando el programa")
        return

    # Stream principal: usamos un Subject y emitimos eventos en un loop async
    source = Subject()

    dashboard_flow = source.pipe(
        moving_average(window=10),
        ops.map(lambda x: Event("MA_UPDATE", x))
    )

    alert_flow = source.pipe(
        detect_pattern(high_volatility_pattern, window_size=5, step=1)
    )

    # =============================================
    # SUSCRIPCIONES Y EJECUCIÓN (versión limpia 2025)
    # =============================================
    print("\n" + "="*60)
    print("   STREAMING REACTIVO DE ACCIONES - TSLA   ".center(60))
    print("="*60 + "\n")

    # Suscripciones (se aplicarán con el scheduler dentro de _run_async)

    print(f"Reproduciendo {len(historical_events)} ticks, uno cada {THROTTLE_INTERVAL}s")
    print("Presiona Ctrl+C para detener\n")

    async def _run_async():
        # Suscribir flujos (callbacks ejecutarán en este hilo de event loop)
        dash_sub = dashboard_flow.subscribe(on_next=print_dashboard_line)
        alert_sub = alert_flow.subscribe(on_next=console_alerter)

        try:
            for ev in historical_events:
                source.on_next(ev)
                # esperar el intervalo (o 0 si se quiere sin throttling)
                await asyncio.sleep(THROTTLE_INTERVAL if THROTTLE_INTERVAL and THROTTLE_INTERVAL > 0 else 0)
            source.on_completed()
        finally:
            try:
                dash_sub.dispose()
            except Exception:
                pass
            try:
                alert_sub.dispose()
            except Exception:
                pass

    try:
        asyncio.run(_run_async())
    except KeyboardInterrupt:
        print("\n\nDetenido por el usuario")

    print("¡Fin del streaming!")


if __name__ == "__main__":
    main()