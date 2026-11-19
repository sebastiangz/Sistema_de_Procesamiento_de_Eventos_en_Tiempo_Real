
from functools import reduce
import time

# Datos iniciales de las criptomonedas
criptomonedas = [
    {"nombre": "Bitcoin", "precio_anterior": 95000, "precio_actual": 98000},
    {"nombre": "Ethereum", "precio_anterior": 3200, "precio_actual": 3100},
    {"nombre": "Solana", "precio_anterior": 180, "precio_actual": 195},
    {"nombre": "Bitcoin", "precio_anterior": 98000, "precio_actual": 92000},
    {"nombre": "Ethereum", "precio_anterior": 3100, "precio_actual": 3300},
    {"nombre": "Solana", "precio_anterior": 195, "precio_actual": 198}
]


# Funcion para calcular el cambio porcentual
def calcular_cambio(evento):
    cambio = (
        (evento["precio_actual"] - evento["precio_anterior"])
        / evento["precio_anterior"]
    ) * 100

    return {
        "nombre": evento["nombre"],
        "precio": evento["precio_actual"],
        "cambio": cambio
    }


# Procesamiento de eventos
def procesar_eventos(eventos):

    print("\n--- PROCESAMIENTO DE EVENTOS FINANCIEROS ---")

    # MAP: calcula el cambio porcentual de cada criptomoneda
    eventos_procesados = list(map(calcular_cambio, eventos))

    # FILTER: selecciona criptomonedas con cambios mayores al 3%
    alertas = list(filter(
        lambda evento: abs(evento["cambio"]) >= 3,
        eventos_procesados
    ))

    # REDUCE: calcula la suma de los precios actuales
    suma_precios = reduce(
        lambda acumulado, evento: acumulado + evento["precio"],
        eventos_procesados,
        0
    )

    # Calcular promedio
    promedio = suma_precios / len(eventos_procesados)

    # Mostrar resultados
    print("\nEVENTOS RECIBIDOS:")

    for evento in eventos_procesados:
        print(
            f'{evento["nombre"]}: '
            f'${evento["precio"]:.2f} | '
            f'Cambio: {evento["cambio"]:.2f}%'
        )

    print("\nALERTAS FINANCIERAS:")

    if alertas:
        for alerta in alertas:
            print(
                f'ALERTA: {alerta["nombre"]} '
                f'tuvo un cambio de {alerta["cambio"]:.2f}%'
            )
    else:
        print("No se detectaron cambios importantes.")

    print(f"\nPromedio de precios: ${promedio:.2f}")


# Simulacion de llegada de eventos en tiempo real
def iniciar_monitoreo():

    print("SISTEMA DE MONITOREO DE CRIPTOMONEDAS")

    for i in range(0, len(criptomonedas), 2):

        # Obtener dos eventos por cada ciclo
        eventos = criptomonedas[i:i + 2]

        procesar_eventos(eventos)

        print("\nEsperando nuevos eventos...")
        time.sleep(2)


# Ejecutar programa
iniciar_monitoreo()
# Archivo inicial
