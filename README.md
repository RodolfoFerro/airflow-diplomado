<center>
   <img src="banner-airflow.png" width="100%">
</center>

Este es el repositorio oficial de las sesiones sobre orquestadores para el Diplomado en Ciencia de Datos de la ENES-UNAM, Unidad León.

### Recursos

- Presentación: [🪧 Google Slides](https://docs.google.com/presentation/d/1433yioRW6FQwErsZpM-PdCrGWtgEuPR9PzwipWBuq8o/pub?start=false&loop=false&delayms=3000)
- DAGs: [/dags](/dags)


### Material adicional

- Instalación de Docker
    - Windows: https://docs.docker.com/desktop/install/windows-install/
    - Mac: https://docs.docker.com/desktop/install/mac-install/
    - Linux: https://docs.docker.com/desktop/install/linux/

- Instalación de Airflow
    - Con `pip`: https://airflow.apache.org/docs/apache-airflow/stable/start.html
    - Con Docker: https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html

- Levantar servicios con Docker: https://airflow.apache.org/docs/apache-airflow/stable/tutorial/pipeline.html#initial-setup

### Configuración

1. Crear una imagen de Docker:
    ```Dockerfile
    FROM apache/airflow:2.10.1-python3.10
    COPY requirements.txt /
    RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt
    ```

2. Construir la imagen:
    ```sh
    docker build . -f Dockerfile --pull --tag ml-container:0.0.1
    ```

3. Descargamos el archivo [`docker-compose.yml`](https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml) y modificar la línea 52 de:
    ```Dockerfile
    image: ${AIRFLOW_IMAGE_NAME:-apache/airflow:2.10.1}
    ```
    a:
    ```Dockerfile
    image: ${AIRFLOW_IMAGE_NAME:-ml-container:0.0.1}
    ```

    > **Remover DAGs de ejemplo:** En línea `61`, cambiar `true` a `false`.

4. Levantar el servicio con:
    ```sh
    docker compose up airflow-init
    docker compose up
    ```