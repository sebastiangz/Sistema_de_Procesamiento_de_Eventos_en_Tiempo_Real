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
- **Librerías**:
  - `RxPY` - Reactive Extensions para Python
  - `asyncio` - Programación asíncrona
  - `toolz` - Utilidades funcionales
  - `streamz` - Processing de streams
  - `dash` - Dashboard en tiempo real

---

## 📦 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/realtime-events-functional.git
cd realtime-events-functional

# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### requirements.txt
```
rxpy>=4.0.0
streamz>=0.6.0
toolz>=0.12.0
asyncio>=3.4.3
dash>=2.14.0
plotly>=5.17.0
websockets>=12.0
```

---

## 🚀 Uso del Sistema

```python
from src.streams import create_event_stream
from src.operators import window, filter, map, merge
from rx import operators as ops

# Crear stream de eventos
events = create_event_stream('sensor_data')

# Pipeline de procesamiento reactivo
processed = (events
    .pipe(ops.filter(lambda e: e.temperature > 30))
    .pipe(ops.map(lambda e: calculate_alert_level(e)))
    .pipe(ops.window_with_time(5.0))  # Ventanas de 5 segundos
    .pipe(ops.flat_map(lambda w: w.pipe(ops.to_list())))
    .pipe(ops.map(aggregate_alerts))
)

# Suscribirse al stream
processed.subscribe(
    on_next=send_alert,
    on_error=log_error,
    on_completed=lambda: print("Stream completed")
)
```

---

## 📂 Estructura del Proyecto

```
realtime-events-functional/
├── src/
│   ├── __init__.py
│   ├── streams.py          # Creación de streams
│   ├── operators.py        # Operadores funcionales
│   ├── patterns.py         # Detección de patrones
│   ├── aggregators.py      # Agregación de eventos
│   ├── alerts.py           # Sistema de alertas
│   └── dashboard.py        # Dashboard en tiempo real
├── tests/
│   ├── test_streams.py
│   ├── test_operators.py
│   └── test_patterns.py
├── examples/
│   ├── sensor_monitoring.py
│   ├── stock_trading.py
│   └── iot_analytics.py
├── docs/
│   ├── frp_concepts.md
│   └── operators_guide.md
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🔑 Características Principales

### 1. Streams Reactivos Funcionales
```python
from rx import Observable
from rx.subject import Subject

class EventStream:
    """Stream de eventos funcional"""
    
    def __init__(self):
        self._subject = Subject()
    
    def emit(self, event):
        """Emitir evento al stream"""
        self._subject.on_next(event)
    
    def pipe(self, *operators):
        """Aplicar operadores funcionales"""
        return self._subject.pipe(*operators)
    
    @staticmethod
    def from_iterable(items):
        """Crear stream desde iterable"""
        return Observable.from_iterable(items)
    
    @staticmethod
    def interval(seconds):
        """Stream de ticks periódicos"""
        return Observable.interval(seconds)
```

### 2. Operadores Composables
```python
from rx import operators as ops
from toolz import compose

# Operador custom: ventana deslizante
def sliding_window(size: int, step: int = 1):
    buffer = []
    
    def operator(source):
        def subscribe(observer, scheduler=None):
            def on_next(value):
                buffer.append(value)
                if len(buffer) >= size:
                    observer.on_next(list(buffer))
                    # Deslizar ventana
                    for _ in range(step):
                        if buffer:
                            buffer.pop(0)
            
            return source.subscribe(
                on_next,
                observer.on_error,
                observer.on_completed,
                scheduler
            )
        return Observable(subscribe)
    return operator

# Composición de operadores
process_sensor = compose(
    ops.filter(lambda e: e.valid),
    ops.map(normalize_reading),
    sliding_window(10, 5),
    ops.map(calculate_statistics)
)
```

### 3. Detección de Patrones Temporales
```python
from dataclasses import dataclass
from typing import List, Callable
import rx.operators as ops

@dataclass
class Pattern:
    """Patrón de eventos a detectar"""
    condition: Callable
    within_seconds: float
    
def detect_pattern(pattern: Pattern):
    """Operador para detectar patrones complejos"""
    def operator(source):
        return source.pipe(
            ops.window_with_time(pattern.within_seconds),
            ops.flat_map(lambda window: 
                window.pipe(
                    ops.to_list(),
                    ops.filter(lambda events: 
                        pattern.condition(events)
                    )
                )
            )
        )
    return operator

# Ejemplo: detectar 3 alertas altas en 10 segundos
high_alert_pattern = Pattern(
    condition=lambda events: sum(e.level == 'HIGH' for e in events) >= 3,
    within_seconds=10.0
)

stream.pipe(detect_pattern(high_alert_pattern))
```

### 4. Backpressure Funcional
```python
from rx import operators as ops

def with_backpressure(buffer_size: int = 100):
    """Implementar backpressure funcional"""
    return ops.compose(
        ops.buffer_with_count(buffer_size),
        ops.flat_map(lambda batch: 
            Observable.from_iterable(batch)
        ),
        ops.throttle_last(0.1)  # Limitar tasa
    )

# Uso
fast_stream.pipe(
    with_backpressure(buffer_size=50),
    ops.map(process_slowly)
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
# Tests
pytest tests/ -v

# Tests de streams reactivos
pytest tests/test_streams.py

# Tests de patrones
pytest tests/test_patterns.py -k "pattern"

# Benchmarks de performance
pytest tests/ -k "benchmark"
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
