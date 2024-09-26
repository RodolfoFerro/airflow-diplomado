"""This is an ML DAG with hyperparameter tuning."""

import pendulum
from airflow.decorators import dag, task


@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["ejemplo", "ml"],
)
def ml_flow():
    """This is the ML DAG."""

    @task(multiple_outputs=True)
    def load_dataset(**kwargs):
        """Loads MNIST Dataset and saves to .npy files."""

        import tensorflow as tf
        import numpy as np

        # Send arguments to DAG
        data = kwargs['dag_run'].conf
        print("[INFO]", data)

        mnist = tf.keras.datasets.mnist
        (training_images, training_labels), (test_images,
                                             test_labels) = mnist.load_data()

        np.save('/tmp/training_images.npy', training_images)
        np.save('/tmp/training_labels.npy', training_labels)
        np.save('/tmp/test_images.npy', test_images)
        np.save('/tmp/test_labels.npy', test_labels)

        data_paths = {
            'training_images_path': '/tmp/training_images.npy',
            'training_labels_path': '/tmp/training_labels.npy',
            'test_images_path': '/tmp/test_images.npy',
            'test_labels_path': '/tmp/test_labels.npy'
        }

        return data_paths

    @task(multiple_outputs=True)
    def preprocess_dataset(data_paths: dict):
        """Task to preprocess dataset from .npy files and saves preprocessed
        data to .npy."""

        import numpy as np

        training_images = np.load(data_paths['training_images_path'])
        test_images = np.load(data_paths['test_images_path'])
        training_labels = np.load(data_paths['training_labels_path'])
        test_labels = np.load(data_paths['test_labels_path'])

        training_images = training_images / 255.0
        test_images = test_images / 255.0

        np.save('/tmp/preprocessed_training_images.npy', training_images)
        np.save('/tmp/preprocessed_test_images.npy', test_images)
        np.save('/tmp/preprocessed_training_labels.npy', training_labels)
        np.save('/tmp/preprocessed_test_labels.npy', test_labels)

        preprocessed_data_paths = {
            'preprocessed_training_images_path':
            '/tmp/preprocessed_training_images.npy',
            'preprocessed_training_labels_path':
            '/tmp/preprocessed_training_labels.npy',
            'preprocessed_test_images_path':
            '/tmp/preprocessed_test_images.npy',
            'preprocessed_test_labels_path':
            '/tmp/preprocessed_test_labels.npy'
        }

        return preprocessed_data_paths

    @task(multiple_outputs=True)
    def split_dataset(preprocessed_data_paths: dict, validation_split=0.2):
        """Divides the dataset into training and testing sets."""

        import numpy as np

        training_images = np.load(
            preprocessed_data_paths['preprocessed_training_images_path'])
        training_labels = np.load(
            preprocessed_data_paths['preprocessed_training_labels_path'])

        num_validation_samples = int(len(training_images) * validation_split)

        validation_images = training_images[:num_validation_samples]
        validation_labels = training_labels[:num_validation_samples]
        training_images = training_images[num_validation_samples:]
        training_labels = training_labels[num_validation_samples:]

        np.save('/tmp/validation_images.npy', validation_images)
        np.save('/tmp/validation_labels.npy', validation_labels)
        np.save('/tmp/training_images_final.npy', training_images)
        np.save('/tmp/training_labels_final.npy', training_labels)

        return {
            'training_images_final': '/tmp/training_images_final.npy',
            'training_labels_final': '/tmp/training_labels_final.npy',
            'validation_images': '/tmp/validation_images.npy',
            'validation_labels': '/tmp/validation_labels.npy'
        }

    @task
    def train_model(dataset_paths: dict, model_params: dict, **kwargs):
        """Trains a classification model using preprocessed data and different
         hyperparameters."""

        import tensorflow as tf
        import numpy as np

        # Send arguments to DAG
        data = kwargs['dag_run'].conf
        print("[INFO]", data)

        training_images = np.load(dataset_paths['training_images_final'])
        training_labels = np.load(dataset_paths['training_labels_final'])
        validation_images = np.load(dataset_paths['validation_images'])
        validation_labels = np.load(dataset_paths['validation_labels'])

        model = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(model_params['units'],
                                  activation=model_params['activation']),
            tf.keras.layers.Dense(10, activation='softmax')
        ])

        model.compile(optimizer=model_params['optimizer'],
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy'])

        model.fit(training_images,
                  training_labels,
                  epochs=model_params['epochs'],
                  validation_data=(validation_images, validation_labels))

        model_path = f"/tmp/mnist_model_{model_params['name']}.h5"
        model.save(model_path)

        return model_path

    @task
    def evaluate_model(model_path: str, test_data_paths: dict, config: dict):
        """Evaluates a trained model using testing data."""

        import tensorflow as tf
        import numpy as np

        model = tf.keras.models.load_model(model_path)
        test_images = np.load(test_data_paths['preprocessed_test_images_path'])
        test_labels = np.load(test_data_paths['preprocessed_test_labels_path'])

        test_loss, test_accuracy = model.evaluate(test_images, test_labels)

        return {
            'model_name': config['name'],
            'model_path': model_path,
            'test_accuracy': test_accuracy,
            'test_loss': test_loss
        }

    @task
    def benchmark_results(results):
        """Genera un reporte de resultados de los diferentes modelos."""

        import pandas as pd

        # Crear un dataframe con los resultados
        df = pd.DataFrame(results)
        df.to_csv('/tmp/benchmark_results.csv', index=False)
        print(df)

    # Configuraciones de hiperparámetros para los tres modelos
    model_configs = [{
        'name': 'model_1',
        'units': 128,
        'activation': 'relu',
        'optimizer': 'adam',
        'epochs': 5
    }, {
        'name': 'model_2',
        'units': 64,
        'activation': 'relu',
        'optimizer': 'sgd',
        'epochs': 5
    }, {
        'name': 'model_3',
        'units': 256,
        'activation': 'tanh',
        'optimizer': 'adam',
        'epochs': 5
    }]

    # DAG flow
    dataset_paths = load_dataset()
    preproc_dataset_paths = preprocess_dataset(dataset_paths)
    split_dataset_paths = split_dataset(preproc_dataset_paths)

    results = []
    for config in model_configs:
        model_path = train_model(split_dataset_paths, config)
        eval_result = evaluate_model(model_path, preproc_dataset_paths, config)
        results.append(eval_result)

    benchmark_results(results)


ml_flow()
