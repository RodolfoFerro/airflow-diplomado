"""
DAG Introductorio a Apache Airflow 3.x
=======================================
Este DAG cubre los conceptos básicos de Airflow:

1. Definición de un DAG con @dag
2. Tareas con @task (TaskFlow API)
3. Paso de datos entre tareas (XCom automático)
4. Parámetros de entrada (dag_run.conf)
5. Dependencias entre tareas
6. Manejo de errores con reintentos
"""

import pendulum
from airflow.sdk import dag, task


@dag(
    dag_id="intro_airflow",
    schedule=None,  # Se ejecuta manualmente
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,  # No ejecutar fechas pasadas
    tags=["intro", "ejemplo"],
    doc_md=__doc__,  # Muestra la docstring en la UI
)
def intro_airflow():

    # ─────────────────────────────────────────
    # CONCEPTO 1: Tarea simple
    # Una tarea es la unidad mínima de trabajo en Airflow.
    # ─────────────────────────────────────────
    @task
    def tarea_inicio():
        """Primera tarea: imprime un mensaje de bienvenida."""
        print("¡Hola desde Airflow 3!")
        return "inicio_completado"

    # ─────────────────────────────────────────
    # CONCEPTO 2: Parámetros de entrada
    # Se pueden pasar parámetros al DAG al ejecutarlo manualmente
    # desde la UI en "Trigger DAG w/ config", por ejemplo:
    # {"nombre": "Estudiante", "repeticiones": 3}
    # ─────────────────────────────────────────
    @task
    def leer_parametros(dag_run=None):
        """Lee parámetros enviados al DAG desde la UI."""
        conf = dag_run.conf if dag_run and dag_run.conf else {}

        nombre = conf.get("nombre", "Mundo")
        repeticiones = conf.get("repeticiones", 1)

        msg = "Parámetros recibidos "
        msg += f"→ nombre: {nombre}, repeticiones: {repeticiones}"
        print(msg)
        return {"nombre": nombre, "repeticiones": repeticiones}

    # ─────────────────────────────────────────
    # CONCEPTO 3: XCom — paso de datos entre tareas
    # El valor que retorna una @task se pasa automáticamente
    # a la siguiente tarea como argumento. Airflow lo almacena
    # internamente usando XCom (cross-communication).
    # ─────────────────────────────────────────
    @task
    def procesar_datos(parametros: dict):
        """Recibe datos de la tarea anterior y los procesa."""
        nombre = parametros["nombre"]
        repeticiones = int(parametros["repeticiones"])

        mensajes = [
            f"Hola, {nombre}! (mensaje {i+1})" for i in range(repeticiones)
        ]

        for msg in mensajes:
            print(msg)

        return mensajes  # Este valor viajará a la siguiente tarea via XCom

    # ─────────────────────────────────────────
    # CONCEPTO 4: Reintentos
    # Si una tarea falla, Airflow puede reintentarla automáticamente.
    # ─────────────────────────────────────────
    @task(
        retries=3,  # Número de reintentos
        retry_delay=pendulum.duration(seconds=5)  # Espera entre reintentos
    )
    def tarea_con_reintentos(mensajes: list):
        """Simula una tarea que podría fallar y usa reintentos."""
        import random

        print(f"Procesando {len(mensajes)} mensajes...")

        # Simulamos un fallo aleatorio con 20% de probabilidad
        # En producción, aquí iría lógica real (llamadas a APIs, etc.)
        if random.random() < 0.5:
            raise ValueError(
                "¡Fallo simulado! Airflow reintentará esta tarea.")

        print("Tarea completada exitosamente.")
        return len(mensajes)

    # ─────────────────────────────────────────
    # CONCEPTO 5: Tarea de cierre
    # Recibe el resultado final y genera un resumen.
    # ─────────────────────────────────────────
    @task
    def tarea_fin(total_mensajes: int):
        """Última tarea: genera un resumen de la ejecución."""
        print("=" * 40)
        print("  RESUMEN DE EJECUCIÓN")
        print("=" * 40)
        print(f"  Mensajes procesados: {total_mensajes}")
        print("  Estado: ✅ Completado")
        print("=" * 40)

    # ─────────────────────────────────────────
    # FLUJO DEL DAG
    # Las dependencias se definen implícitamente al pasar
    # el retorno de una tarea como argumento de la siguiente.
    #
    #  tarea_inicio
    #       ↓
    #  leer_parametros
    #       ↓
    #  procesar_datos
    #       ↓
    #  tarea_con_reintentos
    #       ↓
    #  tarea_fin
    # ─────────────────────────────────────────
    inicio = tarea_inicio()
    parametros = leer_parametros()
    mensajes = procesar_datos(parametros)
    total = tarea_con_reintentos(mensajes)
    tarea_fin(total)

    # Forzamos que leer_parametros espere a tarea_inicio
    inicio >> parametros


intro_airflow()
