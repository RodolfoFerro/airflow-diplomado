"""Sample pipeline."""

import pendulum

from numpy.random import randint
from airflow.decorators import dag, task


@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["ejemplo"],
)
def sample_pipeline():
    """Ejemplo de pipeline."""

    @task
    def genera_edad():
        edad = randint(15, 25)
        return edad

    @task
    def verifica_edad(edad_de_persona: int):
        if edad_de_persona >= 18:
            print("Es mayor de edad")
        print("Es menor de edad")

    edad = genera_edad()
    verifica_edad(edad)

sample_pipeline()
