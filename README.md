# ⚡ Proyecto 5: Sistema de Procesamiento de Eventos en Tiempo Real

## 📋 Descripción del Proyecto

Sistema reactivo funcional para procesar streams de eventos en tiempo real utilizando programación funcional reactiva (FRP), operadores composables y detección de patrones complejos.

**Universidad de Colima - Ingeniería en Computación Inteligente**  
**Materia**: Programación Funcional  
**Profesor**: Gonzalez Zepeda Sebastian  
**Semestre**: Agosto 2025 - Enero 2026

---

## 🎯 Objetivos 

- Implementar **Functional Reactive Programming (FRP)**
- Desarrollar **streams composables** con operadores funcionales
- Aplicar **event sourcing** con funciones puras
- Crear **detectores de patrones** temporales
- Utilizar **backpressure** funcional
- Practicar **hot/cold observables**

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje**: Python 3.11+
- **Paradigma**: Programación Funcional Reactiva
- **Librerías clave**:
    - `rx` (RxPY) - Reactive Extensions para Python
    - `pandas` - manipulación de datos tabulares
    - `plotly` - visualización y generación de dashboards HTML
    - `websockets` - servidor WebSocket opcional para demos
    - `dash` - (opcional) interfaz de dashboard en tiempo real

---

## 📦 Instalación

```bash
# Clonar
git clone https://github.com/sebastiangzSistema_de_Procesamiento_de_Eventos_en_Tiempo_Real.git
cd Sistema_de_Procesamiento_de_Eventos_en_Tiempi_Real

# Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate

# Actualizar pip e instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### requirements.txt (ejemplo mínimo)
```
rx>=3.2.0
pandas>=2.1.0
dash>=2.14.0
plotly>=5.17.0
websockets>=12.0
```

---

## 🚀 Uso del Sistema

```python
# Nota: el paquete `src` NO debe ejecutarse directamente. Importa sus
# utilidades desde los ejemplos en `./examples` o desde tu proyecto.

import sys

if __name__ == "__main__" and __package__ is None:
    print("No ejecutes este archivo directamente. Usa los ejemplos en ./examples o importa el paquete 'src'.")
    print("Ejemplo: python -u examples/pipeline_demo.py  o  MAX_TICKS=20 python -u examples/stock_trading.py")
    sys.exit(0)

# Exporta las utilidades principales del paquete `src` para uso desde
# los ejemplos o desde otros módulos del proyecto.
from .streams import Event, EventStream, create_event_stream, get_async_scheduler
from .operators import (
    scale_event, filter_above, compose_pipeline,
    sliding_window, debounce_window, with_backpressure,
    merge_streams, zip_streams, combine_latest, time_window
)
from .patterns import (
    detect_pattern, Pattern, high_volatility_pattern,
    threshold_pattern, spike_pattern, detect_sequence,
    detect_correlation, cep_operator, ml_anomaly_detector
)
from .aggregators import moving_average
from .alerts import console_alerter, AlertManager, aggregate_alerts
from .dashboard import print_dashboard_line, WebsocketBroadcaster

__all__ = [
    "Event", "EventStream", "create_event_stream", "get_async_scheduler",
    "scale_event", "filter_above", "compose_pipeline",
    "sliding_window", "debounce_window", "with_backpressure",
    "merge_streams", "zip_streams", "combine_latest", "time_window",
    "detect_pattern", "Pattern", "high_volatility_pattern",
    "threshold_pattern", "spike_pattern", "detect_sequence",
    "detect_correlation", "cep_operator", "ml_anomaly_detector",
    "moving_average", "console_alerter", "AlertManager", "aggregate_alerts",
    "print_dashboard_line", "WebsocketBroadcaster"
]

if __name__ == "__main__":
    # Protección: evita ejecutar el initializer del paquete por accidente.
    print("No ejecutes este archivo directamente. Usa los ejemplos en ./examples o importa el paquete 'src'.")
    print("Ejemplo: python -u examples/pipeline_demo.py  o  MAX_TICKS=20 python -u examples/stock_trading.py")
```

---

## 📂 Estructura del Proyecto

```
Sistema_de_Procesamiento_de_Eventos_en_Tiempo_Real/
├── src/
│   ├── `__init__.py`
│   ├── `streams.py`          # Creación de streams
│   ├── `operators.py`        # Operadores funcionales
│   ├── `patterns.py`         # Detección de patrones
│   ├── `aggregators.py`      # Agregación de eventos
│   ├── `alerts.py`           # Sistema de alertas
│   └── `dashboard.py`        # Dashboard en tiempo real
├── tests/
│   ├── `test_streams.py`
│   ├── `test_operators.py`
│   ├── `test_patterns.py`
│   ├── `test_patterns_extra.py`
│   ├── `test_alerts.py`
│   └── `test_alerts_extra.py`
├── examples/
│   ├── `iot_analytics.py`
│   ├── `pipeline_demo.py`
│   ├── `sensor_monitoring.py`
│   └── `stock_trading.py`
├── docs/
│   ├── `frp_concepts.md`
│   ├── `operators_guide.md`
│   └── `references_apa.md`
├── `requirements.txt`
├── `README.md`
└── `.gitignore`
```

---

## 🔑 Características Principales

### 1. Streams Reactivos Funcionales
```python
"""
event_framework_async.py 
"""

import rx
from rx import operators as ops
from rx.subject import Subject

# AsyncIO scheduler (compatible RxPY 3/4)
try:
    from rx.scheduler.eventloop import AsyncIOScheduler
except:
    try:
        from rx.scheduler.eventloop import AsyncIOThreadSafeScheduler as AsyncIOScheduler
    except:
        AsyncIOScheduler = None

from datetime import datetime
import asyncio
from typing import Optional


class Event:
    def __init__(self, typ: str, data: dict):
        self.type, self.data, self.ts = typ, data, datetime.now()
    def __repr__(self):
        return f"<Event {self.type} {self.data} @ {self.ts.strftime('%H:%M:%S')}>"

class EventStream:
    def __init__(self, name: str, subject: Optional[Subject] = None):
        self.name = name
        self._s = subject or Subject()

    def emit(self, ev: Event):
        print(f"[{self.name}] → {ev}")
        self._s.on_next(ev)

    def pipe(self, *ops): return self._s.pipe(*ops)
    def obs(self): return self._s

    @staticmethod
    def hot(name: str): return EventStream(name)

    @staticmethod
    def cold(items): return rx.from_iterable(items)

    @staticmethod
    def share(cold, name: str):
        s = Subject(); cold.subscribe(s); return EventStream(name, s)

    @staticmethod
    def interval(sec: float): return rx.interval(sec)

def stream(name: str) -> EventStream:
    print(f"Stream → {name}")
    return EventStream.hot(name)

def async_scheduler():
    if not AsyncIOScheduler: raise RuntimeError("No AsyncIO scheduler")
    return AsyncIOScheduler(asyncio.get_running_loop())
```

### 2. Operadores Composables
```python
"""
operators.py 
Colección de operadores RxPY útiles 
"""

from rx import operators as ops
from typing import Callable
from .streams import Event  


# ==== Transformaciones ====
scale = lambda factor: ops.map(
    lambda e: Event(e.type, {**e.data, "value": e.data.get("value", 0) * factor})
)

above = lambda thresh: ops.filter(lambda e: e.data.get("value", 0) > thresh)

# ==== Ventanas ====
window = lambda size, step=1: ops.buffer_with_count(size, step)      # sliding
debounce_list = lambda sec: ops.pipe(                                # burst → lista
    ops.debounce(sec), ops.to_list(), ops.filter(bool)
)

# ==== Backpressure simple ====
backpressure = lambda buf=50, every=0.1: ops.pipe(                   # drop oldest
    ops.buffer_with_time(every),
    ops.map(lambda b: b[-buf:] if b else []),
    ops.flat_map(rx.from_iterable)
)

# ==== Retry con backoff exponencial ====
retry = lambda attempts=3, delay=0.5: ops.retry_when(
    lambda errs: errs.pipe(
        ops.zip(rx.range(1, attempts + 1)),
        ops.flat_map(lambda p: rx.timer(delay * (2 ** (p[1] - 1))))
    )
)

# ==== Combinadores de streams ====
merge = rx.merge
zip_ = rx.zip
latest = rx.combine_latest

# ==== Ventana temporal (con fallback) ====
time_win = lambda sec: ops.buffer_with_time(sec)  # lanza excepción si no hay scheduler
```

### 3. Detección de Patrones Temporales
```python
"""
patterns.py 
Detección de patrones CEP + anomalías en streams de Event
"""

from typing import List, Callable
from rx import operators as ops
import rx
from .streams import Event


class Pattern:
    def __init__(self, name: str, check: Callable[[List[Event]], bool]):
        self.name, self.check = name, check
    def __call__(self, win: List[Event]) -> bool:
        return self.check(win)


# ==== Patrones básicos ====
high_vol = Pattern("HIGH_VOL", lambda w: len(w) > 1 and sum(abs(e.data.get("change",0)) for e in w)/len(w) > 2)

threshold = lambda f, th: Pattern(f"THRESH_{f}_{th}", lambda w: any(e.data.get(f,0) > th for e in w))

spike = lambda f, k=2.0: Pattern(f"SPIKE_{f}", lambda w: len(w)>1 and w[-1].data.get(f,0) > sum(e.data.get(f,0) for e in w[:-1])/max(1,len(w)-1) * k)

sequence = lambda types: ops.pipe(
    ops.buffer_with_count(len(types), 1),
    ops.filter(lambda w: [e.type for e in w] == types),
    ops.map(lambda w: {"pattern": "SEQ", "events": w})
)

# ==== Operador universal de deteccion ====
detect = lambda pat, size=5, step=1: ops.pipe(
    ops.buffer_with_count(size, step),
    ops.filter(pat),
    ops.map(lambda w: {"pattern": pat.name, "events": w})
)

# ==== Anomalia Z-score (ML simple) ====
z_anomaly = lambda field, thresh=3.0, win=20: ops.pipe(
    ops.buffer_with_count(win, 1),
    ops.map(lambda w: (
        [e.data.get(field,0) for e in w], w
    )),
    ops.map(lambda pair: (
        vs := pair[0],
        mean := sum(vs)/len(vs),
        std := (sum((v-mean)**2 for v in vs)/len(vs))**0.5 or 1,
        abs(vs[-1] - mean)/std
    )),
    ops.filter(lambda z: z >= thresh),
    ops.map(lambda z: {"pattern": "Z_ANOMALY", "z": z, "value": vs[-1]})
)

# ==== CEP múltiple ultra-simple ====
cep = lambda rules, size=5: ops.pipe(
    ops.buffer_with_count(size, 1),
    ops.flat_map(lambda w: rx.from_iterable(r for r in rules if r(w)))
)
```

### 4. Backpressure Funcional
```python
from rx import operators as ops
import rx
from rx.scheduler import ThreadPoolScheduler  # o get_async_scheduler() si usas asyncio

# Scheduler para no bloquear el productor (opcional pero recomendado)
pool = ThreadPoolScheduler()

def with_backpressure(
    buffer_size: int = 100,
    drop_oldest: bool = True,
    sample_every: float = 0.05  # 50ms → ~20 eventos/seg max si hay presión
):
    """
    Backpressure REAL y robusta para streams rápidos → consumidor lento.
    
    Estrategia ganadora (probada en producción):
    1. on_backpressure_buffer → cola limitada (drop oldest/newest)
    2. sample → limita tasa de entrega al suscriptor lento
    3. observe_on → entrega en thread-pool (nunca bloquea el productor)
    """
    strategy = ops.on_backpressure_drop() if not drop_oldest else ops.on_backpressure_buffer(buffer_size)
    
    return ops.pipe(
        strategy,                         
        ops.sample(sample_every),        
        ops.observe_on(pool),             
    )

# ========================
# Versión asyncio-friendly (la que más uso en demos)
# ========================
from .streams import get_async_scheduler  # tu helper del framework

def with_backpressure_async(buffer_size: int = 100, sample_every: float = 0.05):
    scheduler = get_async_scheduler()
    return ops.pipe(
        ops.on_backpressure_buffer(buffer_size, overflow_strategy="drop_oldest"),
        ops.sample(sample_every, scheduler),
        ops.observe_on(scheduler),
    )
```

---

## 📊 Funcionalidades Implementadas

### Procesamiento de Streams
- ✅ Hot y Cold observables
- ✅ Operadores de transformación (map, filter, reduce)
- ✅ Operadores de combinación (merge, zip, combineLatest)
- ✅ Ventanas temporales y basadas en count

### Detección de Patrones
- ✅ Patrones simples (threshold, spike)
- ✅ Patrones temporales (secuencias, correlaciones)
- ✅ Patrones complejos (CEP - Complex Event Processing)
- ✅ Machine Learning en streams

### Sistema de Alertas
- ✅ Niveles de severidad configurables
- ✅ Agregación de alertas
- ✅ Deduplicación funcional
- ✅ Notificaciones en tiempo real

### Dashboard
- ✅ Visualización en tiempo real
- ✅ Métricas dinámicas
- ✅ Gráficos actualizables
- ✅ WebSockets para updates

---

## 🧪 Testing

```bash

# Activar entorno virtual (equivalente a: source .venv/bin/activate)
.\.venv\Scripts\Activate.ps1

# Ejecutar tests
python -m unittest discover -s tests -p "test_*.py" -v

# Pipeline demo (genera pipeline_dashboard.html)

# export MAX_TICKS = N
$env:MAX_TICKS = "200"

# Ejecutar demo
python examples\pipeline_demo.py

# Abrir dashboard (equivalente a: open pipeline_dashboard.html)
Start-Process ".\pipeline_dashboard.html"

# Stock demo (genera tsla_dashboard.html)

# export MAX_TICKS = N
$env:MAX_TICKS = "300"

# Ejecutar demo
python examples\stock_trading.py

# Abrir dashboard (equivalente a: open tsla_dashboard.html)
Start-Process ".\tsla_dashboard.html"
```

---

## 📈 Pipeline de Desarrollo

### Semana 1: Fundamentos Reactivos (30 Oct - 5 Nov)
- Configuración de RxPY
- Streams básicos
- Operadores fundamentales

### Semana 2: Operadores Avanzados (6 Nov - 12 Nov)
- Composición de operadores
- Backpressure
- Hot/Cold observables

### Semana 3: Patrones y Alertas (13 Nov - 19 Nov)
- Complex Event Processing
- Sistema de alertas
- Integración completa

### Semana 4: Dashboard (20 Nov)
- Visualización en tiempo real
- WebSockets
- Documentación final

---

## 💼 Componente de Emprendimiento

**Aplicación Real**: Plataforma de monitoreo IoT en tiempo real

**Propuesta de Valor**:
- Detección instantánea de anomalías
- Alertas predictivas basadas en patrones
- Escalabilidad horizontal
- Dashboard intuitivo en tiempo real

**Casos de Uso**:
- **Industrial**: Monitoreo de sensores en fábricas
- **Smart Cities**: Análisis de tráfico vehicular
- **Healthcare**: Monitoreo de signos vitales
- **Finance**: Detección de fraude en transacciones

**Modelo de Negocio**: SaaS con pricing por número de eventos/segundo

---

## 📚 Referencias

### Artículos Académicos
- Czaplicki, E. (2012). *Elm: Concurrent FRP for Functional GUIs*
- Bainomugisha, E. et al. (2013). *A Survey on Reactive Programming*

### Documentación Técnica
- **RxPY**: https://rxpy.readthedocs.io/
- **ReactiveX**: http://reactivex.io/
- **Streamz**: https://streamz.readthedocs.io/

### Recursos de Aprendizaje
- André Staltz - Introduction to Reactive Programming
- Erik Meijer - Reactive Extensions course

---

## 🏆 Criterios de Evaluación

- **Streams Reactivos (30%)**: Implementación correcta de FRP
- **Operadores Composables (25%)**: Elegancia, reusabilidad
- **Detección de Patrones (25%)**: Patrones complejos, precisión
- **Dashboard y Visualización (20%)**: UX, tiempo real

---

## 👥 Autores

**Nombre**: [Henry Eduardo Zambrano Cisneros]
            [Irwin Carcaño Gonzalez]
            [Cristofer jesus Gomez Gonzalez ]  
**Email**:  [hzambrano@ucol.mx]
            [icarcano@ucol.mx]
            [cgomez49@ucol.mx]  
**GitHub**: [@eLpXn0chon](https://github.com/eLpXn0chon)
            [@x001rwin](https://github.com/x001rwin)
            [@Cristofer-Gomez](https://github.com/Cristofer-Gomez)
---

## 📄 Licencia

Proyecto académico - Universidad de Colima © 2025
