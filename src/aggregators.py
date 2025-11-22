from rx import operators as ops
from .streams import Event

# Estado inicial inmutable para la agregación
INITIAL_ACC = {"sum": 0.0, "count": 0, "history": []}

def moving_average(window: int = 5):
    """Calcula la media movil simple (SMA) en una ventana deslizante"""
    
    def accumulator(acc, event):
        """Funcion pura que calcula el nuevo estado (inmutable)"""
        price = event.data.get("price", 0)

        # 1. Actualizar el historial con el nuevo precio
        new_history = acc["history"] + [price]

        # 2. Limitar el historial al tamaño de la ventana (inmutabilidad por slicing)
        if len(new_history) > window:
            new_history = new_history[1:] 

        # 3. Recalcular suma y cuenta del nuevo historial
        new_sum = sum(new_history)
        new_count = len(new_history)
        
        # 4. Calcular el MA
        ma = new_sum / new_count if new_count > 0 else price
        
        # Devolver el nuevo estado
        return {
            "symbol": event.data.get("symbol", "N/A"),
            "price": price,
            "ma": ma,
            "sum": new_sum,
            "count": new_count,
            "history": new_history 
        }

    return ops.scan(accumulator, INITIAL_ACC)