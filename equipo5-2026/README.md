# Sistema de Procesamiento de Eventos en Tiempo Real

## Integrantes
* **Brayan Homero Rosales Rodríguez** - 20221238
* **Jose Enrique Ricardo Estrada** - 20221249
* **Leonardo Silva López** - 20220429

## Componente de Emprendimiento
Para este proyecto, hemos seleccionado el Procesamiento de Eventos Financieros en Tiempo Real (Monitoreo de Criptomonedas) como nuestro atractivo de emprendimiento. 

### Caso de Uso: Alertas de Volatilidad en Bitcoin
El sistema simulará un flujo continuo de precios de Bitcoin y emite alertas cuando detecta volatilidad.

---

## Estructura del proyecto
```
equipo5-2026/
├── docs/
│   └── articulos.txt        # Artículos de referencia
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── operadores.py        # Transformaciones sobre el flujo
│   ├── reglas.py            # Reglas de detección de alertas
│   ├── state.py             # Estado entre eventos
│   └── streams.py           # Generación del flujo de precios
├── tests/
│   ├── __init__.py
│   ├── test_operadores.py
│   ├── test_reglas.py
│   └── test_streams.py
├── requirements.txt
└── README.md
```

### Asignación de Trabajo
| Archivo         | Responsable |
|-----------------|-------------|
| `main.py`       | Todos       |
| `operadores.py` | Enrique     |
| `reglas.py`     | Homero      |
| `state.py`      | Leonardo    |
| `streams.py`    | Leonardo    |

---

## Arquitectura del proyecto

*   **`src/streams.py`**: Simula/genera el flujo de precios de Bitcoin. 
*   **`src/operadores.py`**: Transformaciones sobre el flujo.
*   **`src/reglas.py`**: Reglas de detección que generan las alertas. 
*   **`src/state.py`**: Mantiene el estado entre eventos.
*   **`src/main.py`**: Punto de entrada: conecta todos los componentes. 

---

## Ejemplo de salida
```
[10:32:01] Precio BTC: 67,250.00
[10:32:02] Precio BTC: 67,310.50
[10:32:03] !!! ALERTA: variación de 2.4% en 10 s !!!
```

---

## Instalación y ejecución

```bash
git clone https://github.com/sebastiangz/Sistema_de_Procesamiento_de_Eventos_en_Tiempo_Real.git
cd equipo5-2026
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

## Pruebas

```bash
python -m pytest tests/
```