from .streams import Event, EventStream, create_event_stream
from .operators import (
    scale_event, filter_above, compose_pipeline,
    sliding_window, debounce_window, with_backpressure
)
from .patterns import detect_pattern, Pattern, high_volatility_pattern
from .aggregators import moving_average
from .alerts import console_alerter
from .dashboard import print_dashboard_line

__all__ = [
    "Event", "EventStream", "create_event_stream",
    "scale_event", "filter_above", "compose_pipeline",
    "sliding_window", "debounce_window", "with_backpressure",
    "detect_pattern", "Pattern", "high_volatility_pattern",
    "moving_average", "console_alerter", "print_dashboard_line"
]