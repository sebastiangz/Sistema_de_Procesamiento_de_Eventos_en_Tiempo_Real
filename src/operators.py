from rx import operators as ops
from typing import Callable
from .streams import Event
import rx
from rx import operators as ops2
from typing import Iterable

def scale_event(factor: float) -> Callable:
    """Multiplica el valor 'value' del evento por un factor dado"""
    return ops.map(lambda e: Event(
        e.type, 
        {**e.data, "value": e.data.get("value", 0) * factor}
    ))

def filter_above(threshold: float) -> Callable:
    """Filtra eventos cuyo 'value' sea mayor al umbral"""
    return ops.filter(lambda e: e.data.get("value", 0) > threshold)

def compose_pipeline(*operators):
    """Encadena una lista de operadores de RxPy"""
    return lambda source: source.pipe(*operators)

def sliding_window(size: int, step: int = 1):
    """Crea ventanas deslizantes de eventos (lista de Eventos)"""
    return ops.buffer_with_count(size, step)

def debounce_window(seconds: float):
    """Emite una lista de eventos despues de un periodo de silencio"""
    return ops.pipe(
        ops.debounce(seconds),
        ops.to_list(),
        ops.filter(lambda x: len(x) > 0)
    )

def with_backpressure(buffer_size: int = 50, sample_interval: float = 0.1):
    """Aplica contrapresion muestreando el flujo"""
    return ops.pipe(
        ops.buffer_with_count(buffer_size),
        ops.flat_map(lambda batch: ops.from_iterable(batch)),
        ops.sample(sample_interval)
    )


# -------------------------
# Combination helpers
# -------------------------
def merge_streams(*sources):
    """Fusiona múltiples observables en uno solo."""
    return rx.merge(*sources)

def zip_streams(*sources):
    """Zipea múltiples observables en tuplas de valores sincronizados."""
    return rx.zip(*sources)

def combine_latest(*sources):
    """Combina los últimos valores de múltiples observables."""
    return rx.combine_latest(*sources)


def time_window(seconds: float):
    """Crea una ventana basada en tiempo. Si no está disponible, intenta usar buffer_with_count como fallback."""
    try:
        return ops.buffer_with_time(seconds)
    except Exception:
        # Fallback simple: ventana por count aproximada
        return ops.buffer_with_count(int(max(1, seconds)))