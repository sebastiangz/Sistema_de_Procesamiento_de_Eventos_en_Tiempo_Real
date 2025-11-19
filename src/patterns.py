# src/patterns.py
from typing import List, Dict, Any, Callable
from .streams import Event
from rx import operators as ops
import rx

class Pattern:
    """Clase base para la definición de patrones."""
    def __init__(self, name: str, check_func: Callable[[List[Event]], bool]):
        self.name = name
        self.check_func = check_func

    def detect(self, event_window: List[Event]) -> bool:
        return self.check_func(event_window)

# ===============================================
# Función Pura de Verificación de Patrones
# ===============================================

def check_high_volatility(events: List[Event]) -> bool:
    """Detecta alta volatilidad si el cambio promedio en la ventana excede el 2.0%."""
    if len(events) < 2:
        return False
        
    changes = [abs(e.data.get("change", 0)) for e in events]
    avg_change = sum(changes) / len(changes)
    return avg_change > 2.0

# ===============================================
# Definición de Patrón
# ===============================================

high_volatility_pattern = Pattern(
    name="HIGH_VOLATILITY", 
    check_func=check_high_volatility
)

# ===============================================
# Operador de Detección
# ===============================================

def detect_pattern(pattern: Pattern, window_size: int = 5, step: int = 1):
    """Operador que detecta un patrón en ventanas de eventos."""
    def _op(source: rx.Observable):
        return source.pipe(
            ops.buffer_with_count(window_size, step),
            # Mapear la lista de eventos a un diccionario de alerta
            ops.map(lambda window: {
                "pattern": pattern.name,
                "count": len(window),
                "events": window
            }),
            # Filtrar solo si el patrón se cumple
            ops.filter(lambda alert: pattern.detect(alert["events"]))
        )
    return _op


# -------------------------
# Patrones adicionales
# -------------------------
def threshold_pattern(field: str, threshold: float):
    """Devuelve un Pattern que detecta cuando `field` excede `threshold`."""
    def checker(events):
        for e in events:
            if e.data.get(field, 0) > threshold:
                return True
        return False
    return Pattern(name=f"THRESHOLD_{field}_{threshold}", check_func=checker)


def spike_pattern(field: str, spike_factor: float = 2.0):
    """Detecta un spike si el valor actual es mayor que la media histórica por `spike_factor`."""
    def checker(events):
        if len(events) < 2:
            return False
        vals = [e.data.get(field, 0) for e in events]
        avg = sum(vals[:-1]) / max(1, len(vals[:-1]))
        return vals[-1] > avg * spike_factor
    return Pattern(name=f"SPIKE_{field}", check_func=checker)


def detect_sequence(expected_types: list, window_size: int = None):
    """Operador que detecta secuencias de tipos de eventos en orden."""
    window_size = window_size or len(expected_types)

    def _op(source: rx.Observable):
        return source.pipe(
            ops.buffer_with_count(window_size, 1),
            ops.filter(lambda win: [e.type for e in win] == expected_types),
            ops.map(lambda win: {"pattern": "SEQUENCE", "events": win, "count": len(win)})
        )
    return _op


def detect_correlation(field_a: str, field_b: str, threshold: float):
    """Detecta correlación simple entre dos campos en la ventana (covarianza simplificada)."""
    def checker(events):
        vals_a = [e.data.get(field_a, 0) for e in events]
        vals_b = [e.data.get(field_b, 0) for e in events]
        if len(vals_a) < 2:
            return False
        # Pearson corr (numerador only simplified)
        mean_a = sum(vals_a) / len(vals_a)
        mean_b = sum(vals_b) / len(vals_b)
        num = sum((a - mean_a) * (b - mean_b) for a, b in zip(vals_a, vals_b))
        # Normalize loosely
        denom = (sum((a - mean_a) ** 2 for a in vals_a) * sum((b - mean_b) ** 2 for b in vals_b)) ** 0.5
        if denom == 0:
            return False
        corr = abs(num / denom)
        return corr >= threshold
    return Pattern(name=f"CORR_{field_a}_{field_b}", check_func=checker)


def cep_operator(rules: list, window_size: int = 5):
    """Operador CEP simple: aplica una lista de funciones que reciben la ventana y devuelven alertas."""
    def _op(source: rx.Observable):
        return source.pipe(
            ops.buffer_with_count(window_size, 1),
            ops.flat_map(lambda win: rx.from_iterable([r(win) for r in rules if r(win)]))
        )
    return _op


# -------------------------
# Machine Learning (simple)
# -------------------------
def ml_anomaly_detector(field: str, z_thresh: float = 3.0, window: int = 20):
    """Operador que marca anomalías simples usando Z-score sobre una ventana deslizante."""
    def _op(source: rx.Observable):
        def to_value(e):
            return e.data.get(field, 0)

        def detect(window_vals, window_events):
            if len(window_vals) < 2:
                return None
            mean = sum(window_vals) / len(window_vals)
            var = sum((v - mean) ** 2 for v in window_vals) / len(window_vals)
            std = var ** 0.5
            last = window_vals[-1]
            z = abs((last - mean) / (std if std > 0 else 1))
            if z >= z_thresh:
                return {"pattern": "ML_ANOMALY", "z": z, "events": window_events}
            return None

        return source.pipe(
            ops.buffer_with_count(window, 1),
            ops.map(lambda win: ( [to_value(e) for e in win], win )),
            ops.map(lambda pair: detect(pair[0], pair[1])),
            ops.filter(lambda x: x is not None)
        )
    return _op