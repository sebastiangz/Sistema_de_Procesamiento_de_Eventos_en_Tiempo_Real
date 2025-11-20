#!/usr/bin/env python3
# Simulacion de un sistema de monitorizacion de temperatura IoT
import os
import sys
SCRIPT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import rx
import time
from rx import operators as ops
from rx.scheduler.mainloop import AsyncioScheduler 
import asyncio
import random

from src.streams import Event
from src.operators import filter_above, debounce_window
from src.alerts import console_alerter

# 1.Flujo de datos IoT simulado 

def generate_temp_data(i):
    """Genera lecturas de temperatura simuladas"""
    # Simula picos de temperatura periodicamente
    temp = 20.0 + random.uniform(-1.0, 1.0)
    if i % 7 == 0:
        temp = 35.0 + random.uniform(0, 5.0) # Pico de temperatura
        
    return Event("TEMP_READING", {"sensor_id": "SENS_001", "temp": temp, "value": temp})

temp_stream = rx.interval(0.3).pipe(
    ops.map(generate_temp_data)
)

# 2 Pipeline de alerta de sobrecarga (debounce) 
# Usamos debounce_window para alertar solo si la temperatura esta alta
# y luego permanece alta (es decir, el flujo de eventos alto se detiene por 2 segundos, 
# lo que indica que el sistema esta estable en un estado de fallo).

OVERHEAT_THRESHOLD = 30.0

overheat_alert_flow = temp_stream.pipe(
    # Filtrar solo si la temperatura excede el umbral
    filter_above(OVERHEAT_THRESHOLD), 
    
    # Agrupar los eventos altos y emitirlos solo si hay 2 segundos de silencio
    debounce_window(2.0), 
    
    # Transformar la lista de eventos en un objeto de alerta simple
    ops.map(lambda window: {
        "pattern": "OVERHEAT_STABLE",
        "count": len(window),
        "events": window 
    })
)

# 3 Suscripción 
print("="*60)
print(" MONITOREO DE SENSORES (Alerta por Sobrecarga Estabilizada) ")
print("="*60)

overheat_alert_flow.subscribe(
    on_next=console_alerter,
    on_error=lambda e: print(f"Error en Alertas: {e}")
)

# Para visualizar los eventos brutos que pasan el filtro (opcional)
temp_stream.pipe(
    filter_above(OVERHEAT_THRESHOLD),
    ops.take(20) # Tomar solo 20 eventos altos para que termine
).subscribe(
    on_next=lambda e: print(f"[Filtro] ⚠️ Temp alta: {e.data['temp']:.2f}°C"),
    on_completed=lambda: print("\nSistema de monitoreo de sensores completado.")
)

# Ejecucion
try:
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    print("\nMonitoreo detenido.")
finally:
    pass # No cerramos el loop si usamos run_forever sin control