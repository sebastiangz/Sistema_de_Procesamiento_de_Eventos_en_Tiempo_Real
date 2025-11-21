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
    """Aplica contrapresion rudimentaria: agrupa por intervalo de tiempo, recorta
    el batch a `buffer_size` (drop_oldest) y emite los elementos.

    - `buffer_size`: máximo número de elementos que se mantendrán por intervalo
    - `sample_interval`: ventana temporal (segundos) para agrupar eventos
    """
    def _op(source):
        return source.pipe(
            ops.buffer_with_time(sample_interval),
            ops.map(lambda batch: batch[-buffer_size:] if batch else []),
            ops.flat_map(lambda batch: rx.from_iterable(batch))
        )
    return _op


def retry_with_backoff(max_retries: int = 3, base_delay: float = 0.5):
    """Operador que reintenta en caso de error con backoff exponencial.

    Usa `retry_when` combinando el stream de errores con delays crecientes.
    """
    def _op(source):
        def notifier(errors):
            # errors paired with attempt number 1..max_retries
            return errors.pipe(
                ops.zip(rx.range(1, max_retries + 1)),
                ops.flat_map(lambda pair: rx.timer(base_delay * (2 ** (pair[1] - 1))))
            )

        return source.pipe(ops.retry_when(notifier))

    return _op


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