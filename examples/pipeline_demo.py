"""Pipeline demo: stream -> aggregator -> pattern -> AlertManager -> dashboard/ws

Ejecuta desde la raíz del repo:
  source .venv/bin/activate
  python examples/pipeline_demo.py
"""
import os
import sys
SCRIPT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import time
import rx
from rx import operators as ops
from src.streams import EventStream, Event
from src.aggregators import moving_average
from src.patterns import threshold_pattern, detect_pattern
from src.alerts import AlertManager
from src.dashboard import websocket_broadcaster_factory, print_dashboard_line, build_six_panel_figure, save_dashboard_html


def main():
    s = EventStream.hot_subject("demo_pipeline")

    # Alert manager
    am = AlertManager(dedup_seconds=3)
    am.subscribe(lambda a: print("[AM] Notified:", a))

    # Websocket (fallback to console)
    ws = websocket_broadcaster_factory()
    ws_started = ws.start()
    print("WS active:", ws_started)

    # Pipeline: compute moving average on price, then map to Event and print
    # Collect series for dashboard
    prices = []
    mas = []
    volumes = []
    changes = []
    anomalies = []
    alerts_count = []

    def _collect_and_print(st):
        data = st if isinstance(st, dict) else st.data
        price = data.get("price", 0)
        ma = data.get("ma")
        vol = data.get("volume", 0)
        ch = data.get("change", 0)
        prices.append(price)
        mas.append(ma if ma is not None else price)
        volumes.append(vol)
        changes.append(ch)
        # anomalies and alerts_count are demo placeholders
        anomalies.append(0)
        alerts_count.append(0)
        print_dashboard_line(Event("MA_UPDATE", data))

    s.as_observable().pipe(
        moving_average(window=3),
        ops.map(lambda st: st if isinstance(st, dict) else st)
    ).subscribe(on_next=_collect_and_print)

    # Pattern: threshold on 'price' > 105 (demo)
    pat = threshold_pattern("price", 105)
    s.as_observable().pipe(
        detect_pattern(pat, window_size=2)
    ).subscribe(lambda alert: am.notify(alert))

    # Emit a few events
    for p in [100, 102, 106, 108, 103, 110]:
        s.emit(Event("TICK", {"symbol": "DEMO", "price": float(p), "change": 0.0}))
        time.sleep(0.2)

    # Broadcast a metric
    ws.broadcast({"type": "demo_complete", "events": 6})

    # Build and save dashboard with collected series
    try:
        series = {
            "Price": prices,
            "MA": mas,
            "Volume": volumes,
            "Change": changes,
            "Anomaly": anomalies,
            "Alerts": alerts_count,
        }
        fig = build_six_panel_figure(series, title="Pipeline Demo Dashboard")
        save_dashboard_html(fig, path="pipeline_dashboard.html")
        print("Saved dashboard: pipeline_dashboard.html")
    except Exception as e:
        print("Could not build dashboard:", e)

    # Stop websocket if active
    if ws_started:
        ws.stop()


if __name__ == "__main__":
    main()
