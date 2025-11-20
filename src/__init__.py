import sys

# Si este archivo se ejecuta directamente (no como paquete), mostrar mensaje
# y salir antes de intentar importaciones relativas que fallarían.
if __name__ == "__main__" and __package__ is None:
    print("No ejecutes este archivo directamente. Usa los ejemplos en ./examples o importa el paquete 'src'.")
    print("Ejemplo: python -u examples/pipeline_demo.py  o  MAX_TICKS=20 python -u examples/stock_trading.py")
    sys.exit(0)

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
from .dashboard import print_dashboard_line, websocket_broadcaster_factory

__all__ = [
    "Event", "EventStream", "create_event_stream", "get_async_scheduler",
    "scale_event", "filter_above", "compose_pipeline",
    "sliding_window", "debounce_window", "with_backpressure",
    "merge_streams", "zip_streams", "combine_latest", "time_window",
    "detect_pattern", "Pattern", "high_volatility_pattern",
    "threshold_pattern", "spike_pattern", "detect_sequence",
    "detect_correlation", "cep_operator", "ml_anomaly_detector",
    "moving_average", "console_alerter", "AlertManager", "aggregate_alerts",
    "print_dashboard_line", "websocket_broadcaster_factory"
]


if __name__ == "__main__":
    # Protección: evita ejecutar el initializer del paquete por accidente.
    # El paquete `src` es una librería de utilidades — usa los ejemplos en
    # la carpeta `examples/` o importa el paquete desde tu proyecto en lugar de
    # ejecutar este archivo directamente.
    print("No ejecutes este archivo directamente. Usa los ejemplos en ./examples o importa el paquete 'src'.")
    print("Ejemplo: python -u examples/pipeline_demo.py  o  MAX_TICKS=20 python -u examples/stock_trading.py")