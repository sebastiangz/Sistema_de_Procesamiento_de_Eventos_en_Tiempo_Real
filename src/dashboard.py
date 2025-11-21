from datetime import datetime
from typing import Dict, Any
from typing import Dict, Any

# Optional plotting helpers
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except Exception:
    PLOTLY_AVAILABLE = False


def print_dashboard_line(event):
    """Suscriptor que imprime una lInea formateada para el dashboard"""
    data: Dict[str, Any] = event.data
    symbol = data.get("symbol", "N/A")
    price = data.get("price", 0)
    change = data.get("change", 0)

    # Intenta obtener el MA si existe (desde aggregators)
    ma = data.get("ma")
    ma_str = f"| MA: {ma:8.2f}" if ma is not None else ""

    status = "SUBE" if change > 0 else "BAJA" if change < 0 else "ESTABLE"

    print(f"{datetime.now().strftime('%H:%M:%S')} | {symbol:6} | ${price:8.2f} | {change:+6.2f}% | {status:8} {ma_str}")


class WebsocketBroadcaster:
    """Encapsula un servidor WebSocket opcional con API start/stop/broadcast.

    Si `websockets` no está instalado o el servidor no puede iniciarse, entra en
    modo 'fallback' donde `broadcast()` imprime por consola.
    """
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self._server = None
        self._clients = set()
        self._loop = None
        self._active = False
        try:
            import websockets  # type: ignore
            self._websockets = websockets
        except Exception:
            self._websockets = None

    async def _handler(self, ws, path):
        self._clients.add(ws)
        try:
            await ws.wait_closed()
        finally:
            self._clients.discard(ws)

    def start(self):
        if not self._websockets:
            self._active = False
            return False
        import asyncio

        # Create server lazily on explicit start
        if self._server is not None:
            return True

        # Ensure there is an event loop for this thread
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self._loop = loop
        try:
            # If the loop is already running (e.g., embedded environment), create the server
            # without blocking the thread. Otherwise, run until complete.
            if self._loop.is_running():
                # schedule coroutine to start server; don't block waiting for it here
                try:
                    coro = self._websockets.serve(self._handler, self.host, self.port)
                    # create task on the running loop
                    self._loop.create_task(coro)
                    self._active = True
                    return True
                except Exception:
                    self._active = False
                    self._server = None
                    return False
            else:
                self._server = self._loop.run_until_complete(
                    self._websockets.serve(self._handler, self.host, self.port)
                )
                self._active = True
                return True
        except Exception:
            self._active = False
            self._server = None
            return False

    def stop(self):
        if not self._server:
            return
        try:
            self._server.close()
            self._loop.run_until_complete(self._server.wait_closed())
        except Exception:
            pass
        self._server = None
        self._active = False

    def broadcast(self, message: dict):
        """Envía mensaje a todos los clientes conectados (async) o imprime en fallback."""
        import json
        if not self._websockets or not self._active or not self._clients:
            # fallback print
            print("[WS BROADCAST]:", message)
            return

        payload = json.dumps(message)
        import asyncio

        async def _send_all():
            await asyncio.gather(*(c.send(payload) for c in list(self._clients)), return_exceptions=True)

        try:
            self._loop.create_task(_send_all())
        except Exception:
            # If we can't schedule, fallback
            print("[WS BROADCAST ERROR] fallback ->", message)


def websocket_broadcaster_factory(host: str = "localhost", port: int = 8765):
    """Factory que devuelve una instancia controlable de `WebsocketBroadcaster`.

    Uso:
      ws = websocket_broadcaster_factory()
      ws.start()   # intenta levantar servidor (si websockets disponible)
      ws.broadcast({...})
      ws.stop()
    """
    return WebsocketBroadcaster(host, port)


def build_six_panel_figure(series_dict: Dict[str, Any], title: str = "Dashboard"):
    """Construye una figura Plotly con hasta 6 subplots (3 filas x 2 columnas).

    `series_dict` debe ser un dict con hasta 6 entradas. Cada entrada puede ser:
      - una tupla `(x_list, y_list)`
      - una lista/iterable `y_list` (x será índice)

    Retorna la figura Plotly. Si Plotly no está disponible lanza RuntimeError.
    """
    if not PLOTLY_AVAILABLE:
        raise RuntimeError("Plotly no está instalado en el entorno. Instala `plotly` para usar las gráficas.")

    # Crear figura 3x2
    fig = make_subplots(rows=3, cols=2, subplot_titles=list(series_dict.keys())[:6])

    items = list(series_dict.items())[:6]
    for idx, (name, series) in enumerate(items):
        row = idx // 2 + 1
        col = idx % 2 + 1

        if isinstance(series, tuple) and len(series) >= 2:
            x, y = series[0], series[1]
        else:
            y = list(series)
            x = list(range(len(y)))

        trace = go.Scatter(x=x, y=y, mode='lines+markers', name=name)
        fig.add_trace(trace, row=row, col=col)

    fig.update_layout(height=900, width=1200, title_text=title, showlegend=False)
    return fig


def save_dashboard_html(fig, path: str = "dashboard.html"):
    """Guarda la figura Plotly en un HTML auto-contenido para la presentación."""
    if not PLOTLY_AVAILABLE:
        raise RuntimeError("Plotly no está instalado en el entorno. Instala `plotly` para usar las gráficas.")
    fig.write_html(path, include_plotlyjs='cdn')
    return path