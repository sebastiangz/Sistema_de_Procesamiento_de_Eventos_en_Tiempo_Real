
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, List, Optional


def console_alerter(alert: Dict[str, Any]):
    """Suscriptor que imprime una alerta formateada en la consola"""
    print("\n" + "═" * 70)
    print(f" ALERTA DETECTADA [{datetime.now().strftime('%H:%M:%S')}] ")
    print(f" Patrón: {alert.get('pattern')}")
    print(f" Detalle: {alert.get('detail', '')}")
    if 'count' in alert:
        print(f" Eventos en ventana: {alert['count']}")
    print("═" * 70 + "\n")


class AlertManager:
    """Maneja deduplicacion, agregación y notificaciones de alertas

    - `notify(alert)` procesa y entrega alertas a los suscriptores
    - deduplication window evita repetición en un periodo corto
    - aggregation agrupa alertas por tipo en un intervalo
    """
    def __init__(self, dedup_seconds: int = 10):
        self.dedup_seconds = dedup_seconds
        self._seen = {}  # key -> timestamp
        self.subscribers: List[Callable[[Dict[str, Any]], None]] = [console_alerter]

    def _is_duplicate(self, key: str) -> bool:
        now = datetime.now()
        last = self._seen.get(key)
        if last and now - last < timedelta(seconds=self.dedup_seconds):
            return True
        self._seen[key] = now
        return False

    def subscribe(self, fn: Callable[[Dict[str, Any]], None]):
        if fn not in self.subscribers:
            self.subscribers.append(fn)

    def notify(self, alert: Dict[str, Any]):
        key = f"{alert.get('pattern')}|{alert.get('detail','')}"
        if self._is_duplicate(key):
            return
        for s in self.subscribers:
            try:
                s(alert)
            except Exception:
                # no romper el flujo por errores en notificaciones
                pass


def aggregate_alerts(alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Agrega una lista de alertas en una sola estructura (simple)."""
    if not alerts:
        return {}
    patterns = {}
    for a in alerts:
        p = a.get('pattern', 'UNKNOWN')
        patterns.setdefault(p, 0)
        patterns[p] += 1
    return {"aggregated_at": datetime.now().isoformat(), "counts": patterns}