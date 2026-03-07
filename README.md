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

1. Creamos un archivo `Dockerfile` con la imagen de Docker:
    ```Dockerfile
    FROM apache/airflow:3.1.7
    COPY requirements.txt /
    RUN pip install --no-cache-dir -r /requirements.txt
    ```

    Y un archivo `.env` con lo siguiente:
    ```
    AIRFLOW_UID=501
    AIRFLOW_IMAGE_NAME=ml-container:0.0.2
    _AIRFLOW_WWW_USER_USERNAME=airflow
    _AIRFLOW_WWW_USER_PASSWORD=airflow
    AIRFLOW__CORE__LOAD_EXAMPLES=false
    ```

2. Construimos la imagen:
    ```sh
    docker build . -f Dockerfile --pull --tag ml-container:0.0.2
    ```

3. Descargamos el archivo [`docker-compose.yml`](https://airflow.apache.org/docs/apache-airflow/3.1.7/docker-compose.yaml):
    ```bash
    curl -LfO 'https://airflow.apache.org/docs/apache-airflow/3.1.7/docker-compose.yaml'
    ```

4. Levantamos el servicio con:
    ```sh
    docker compose up airflow-init
    docker compose up
    ```