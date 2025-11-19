from datetime import datetime
from typing import Dict, Any
from typing import Dict, Any


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


# Simple WebSocket broadcaster (opcional)
def websocket_broadcaster_factory(host: str = 'localhost', port: int = 8765):
    """Devuelve un objeto con interfaz `broadcast(message)` si `websockets` está instalado.

    Esta función es un *stub* seguro: si no está disponible la dependencia, devuelve
    una implementación que imprime los mensajes en consola.
    """
    try:
        import asyncio
        import json
        import websockets

        clients = set()

        async def handler(ws, path):
            clients.add(ws)
            try:
                await ws.wait_closed()
            finally:
                clients.remove(ws)

        async def start_server():
            return await websockets.serve(handler, host, port)

        loop = asyncio.get_event_loop()
        loop.create_task(start_server())

        def broadcast(message: dict):
            payload = json.dumps(message)
            async def _send_all():
                await asyncio.gather(*(c.send(payload) for c in list(clients)), return_exceptions=True)
            try:
                asyncio.get_event_loop().create_task(_send_all())
            except Exception:
                pass

        return {"broadcast": broadcast, "active": True}

    except Exception:
        # Fallback: imprime en consola si no hay websockets
        def broadcast(message: dict):
            print("[WS BROADCAST]:", message)

        return {"broadcast": broadcast, "active": False}