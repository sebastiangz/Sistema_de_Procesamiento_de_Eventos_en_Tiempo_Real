# 🛠️Guía de operadores personalizados 

Nuestros operadores personalizados facilitan la creación de pipelines complejos y reutilizables.

## 1. Transformación y Filtrado (Semana 1)

| Operador | Operador RxPy Base | Uso |
| :--- | :--- | :--- |
| `scale_event(factor)` | `ops.map` | Multiplica un campo del evento (ej. 'value') por un factor. |
| `filter_above(threshold)`| `ops.filter` | Descarta eventos donde el valor es menor o igual al umbral. |
| `compose_pipeline(*ops)`| N/A | Función de utilidad para agrupar y encadenar múltiples operadores RxPy. |

## 2. Windowing y Control de Flujo (Semana 2)

| Operador | Operador RxPy Base | Propósito |
| :--- | :--- | :--- |
| `sliding_window(size, step)`| `ops.buffer_with_count`| Agrupa eventos en ventanas deslizantes. Es la base para `detect_pattern`. |
| `debounce_window(seconds)`| `ops.debounce`, `ops.to_list`| Útil para emitir notificaciones solo después de un período de "silencio" en el flujo (ej. alerta de fallo masivo después de 5 segundos sin eventos). |
| `with_backpressure(size, interval)`| `ops.sample`, `ops.buffer`| Previene la saturación del consumidor. Almacena eventos y luego solo muestrea el flujo a un ritmo constante. |

## 3. Agregación

| Operador | Operador RxPy Base | Propósito |
| :--- | :--- | :--- |
| `moving_average(window)`| `ops.scan` | Calcula una media móvil sobre la propiedad 'price', manteniendo el estado del historial en la ventana. |