#!/usr/bin/env python3
# Simulación de analitica avanzada IoT con backpressure
import os
import sys
SCRIPT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import rx
import time
from rx import operators as ops
import asyncio
from rx.scheduler.mainloop import AsyncioScheduler 
import random

from src.streams import Event
from src.operators import with_backpressure
from src.dashboard import print_dashboard_line

# 1 Flujo de Datos IoT rapido (alto Volumen) 

def generate_high_volume_data(i):
    """Genera datos de alto volumen, simulando sobrecarga."""
    return Event("READING", {"device_id": f"D_{i%5}", "value": i, "price": random.uniform(10, 20), "change": 0})

# Emitir datos muy rapido (cada 50ms)
high_volume_stream = rx.interval(0.05).pipe(
    ops.take(500), # Tomar 500 eventos
    ops.map(generate_high_volume_data)
)

# 2 Pipeline con contrapresion
# Usamos with_backpressure para que el consumidor (print_dashboard_line) 
# no se sature al procesar 500 eventos en segundos

# Tomara lotes de 20 eventos y muestreara a un evento cada 0.5 segundos
controlled_flow = high_volume_stream.pipe(
    with_backpressure(buffer_size=20, sample_interval=0.5) 
)

# 3 Suscripcion y comparacion

print("="*60)
print(" ANALITICA IOT CON CONTRAPRESION (Backpressure) ")
print("="*60)

# Suscripcion 1: flujo Normal (rapido, puede saturar la consola)
print("\n--- FLUJO BRUTO (Sin control) ---")
high_volume_stream.pipe(ops.take(10)).subscribe(
    on_next=lambda e: print(f"  [Bruto] -> Evento {e.data['value']}"),
    on_completed=lambda: print("  [Bruto] -> COMPLETO")
)

# Suscripcion 2: Flujo controlado
print("\n--- FLUJO CONTROLADO (muestreado) ---")
controlled_flow.subscribe(
    on_next=lambda e: print(f"  [CONTROLADO] -> Valor: {e.data['value']}"),
    on_completed=lambda: print("\nSistema de analitica IoT completado.")
)


# Ejecucion
# Aqui la fuente principal es high_volume_stream que tiene un take(500), 
# el programa terminara automaticamente.
try:
    high_volume_stream.run(scheduler=AsyncioScheduler(asyncio.get_event_loop()))
except KeyboardInterrupt:
    print("\nAnalítica detenida.")
except Exception as e:
    print(f"Error: {e}")