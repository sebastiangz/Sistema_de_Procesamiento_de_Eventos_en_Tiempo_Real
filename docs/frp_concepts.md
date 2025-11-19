# Fundamentos de la programación funcional reactiva (FRP)

La Programacion Funcional Reactiva (FRP) es un paradigma de programacion para manejar flujos de datos asincronos utilizando el modelo de **Observable/Observer**.

# 1 Conceptos Clave

# A Flujos de eventos (observables)
Un observable es una coleccion de elementos que llegan a lo largo del tiempo, es la fuente de datos. En este proyecto, `EventStream` es nuestro Observable base que emite objetos `Event`

# B Funciones puras (operadores)
Los operadores son funciones que se aplican a los Observables para transformarlos, filtrarlos o combinarlos, los operadores deben ser **funciones puras**:
* No modifican el estado externo
* Dada la misma entrada siempre producen la misma salida
* En RxPy se usan para encadenar (`.pipe()`) transformaciones inmutables (`map`, `filter`, `scan`)

# C Inmutabilidad
Es fundamental que los operadores no modifiquen los `Event` en su lugar, un operador siempre debe crear un **nuevo objeto `Event`** o un nuevo objeto de estado (`acc` en `scan`) para garantizar la trazabilidad y evitar efectos secundarios.

# D Observer (suscriptor)
Es la entidad que consume el flujo de datos, implementa los metodos `on_next` (maneja el dato) `on_error` (maneja fallos) y `on_completed` (maneja el cierre del flujo), en nuestro proyecto `console_alerter` y `print_dashboard_line` actuan como observers

# 2 Ventanas de Tiempo (windowing)

Para la deteccion de patrones, es necesario agrupar eventos en funcion del tiempo o el conteo, usamos `ops.buffer_with_count` para crear "ventanas" (listas) de eventos para su analisis, lo que nos permite calcular métricas como la media movil o la volatilidad sobre un conjunto finito de datos