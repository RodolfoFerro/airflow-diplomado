"""Main data flow."""

from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from pendulum import datetime


def machine_learning_task():
    """A ML function that will be executed as a PythonOperator task."""

    import tensorflow as tf
    import pandas as pd

    # Load data
    circles = pd.read_csv('circles.csv')
    x = circles[['x1', 'x2']]
    y = circles[['label']]

    # Create model
    model = tf.keras.Sequential([
        tf.keras.layers.Input([2]),
        tf.keras.layers.Dense(4, activation='tanh'),
        tf.keras.layers.Dense(2, activation='tanh'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

    loss = tf.keras.losses.BinaryCrossentropy()
    optimizer = tf.keras.optimizers.Adam(learning_rate=3e-3)
    model.compile(loss=loss, optimizer=optimizer, metrics=['accuracy'])
    _ = model.fit(x, y, epochs=100)

    print('Evaluación del modelo:', model.evaluate(x, y))


# Define the DAG
@dag(
    dag_id="machine_learning_dag",
    description="DAG to execute a simple ML task.",
    start_date=datetime(2021, 1, 1, tz="UTC"),
    schedule_interval="@daily",
    catchup=False,
    tags=["ml"]
)
def ml_dag():
    """ML Dataflow to define DAG."""

    # Define the tasks
    task_bash = BashOperator(task_id="bash_task",
                             bash_command="""
            echo "Ejecutando un script desde bash..."
            # python /path/to/script.py
        """)

    @task
    def dataset_creation_task():
        """A data function to create a synthetic dataset."""

        from sklearn.datasets import make_circles
        import pandas as pd

        # Make 1000 examples
        n_samples = 1000

        # Create circles
        x, y = make_circles(n_samples, noise=0.03, random_state=42)
        circles = pd.DataFrame({"x1": x[:, 0], "x2": x[:, 1], "label": y})
        circles.to_csv('circles.csv')

    task_python = PythonOperator(task_id="python_ML",
                                 python_callable=machine_learning_task)

    # Set task dependencies
    task_bash >> dataset_creation_task() >> task_python

ml_dag()