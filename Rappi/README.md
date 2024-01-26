# Challenge for MLE Role @Rappi

Refer to file [Rappi - MLE Challenge.md](Rappi%20-%20MLE%20Challenge.md)
The goal of this repository is to show a basic architecture for an ML project. The emphasis is not on ML but rather on setting up a repository with goof practices.

## Setting up the IDE

If using vscode you can use the launch and settings parameters defined in .vscode . Notice that for compatibility with pytest you may have to create a .env file in this folder containing

    ```makefile
    PYTHONPATH="<absolute path to the rootdirectory of this project on your machine>"
    ```

## Packaging

This repository uses the following tools

- black, flake8, isort for formating
- poetry and anaconda to manage the environment dependencies
- coverage and pytest for unit-testing within the folder tests
- pyproject.toml to centralize all of these tools' parameters

## Formating, tests, shortcuts

You can use the makefile pre-made commands to format the code and run tests. The commands from the makefile must be run from the project's root.
I have done only basic testing so far just for the sake of showing I know how.
`make run-tests` includes a coverage report.

## Notebook and CLI

main.ipynb can be run and includes comments about the different steps. Code can also be run from the CLI in 2 ways:

- executing python then importing the "code" module. This allows for interactive use of the functions.
- running command `python main.py` will execute the corresponding file

## Architecture of the solutions

We divide the problems into the following main parts:

- Getting the dataset
- Analysing and preprocessing the dataset
- Creating an estimator
- a training pipeline
- an evaluation module
- a prediction pipeline.

I created corresponding modules that are adaptable in the future for each of these tasks. They may not be relevant as is (the titanic ML problem can be solved with barely a couple lines of code after all), but show a good example of OOP practices.

## Analysis

- Refer to the [notebook](main.ipynb) for feature importance and model performance analysis

## Putting into production

Here are the next stages to put this into production.

- Creating a proper framework for environment variables. Omegaconf and hydra can be used to gather information like model_path, dates etc from both a local and remote dev environment.
- Making sure the system can be test both locally and remotely
- Setting pre-commit like checks for CI/CD (formating, but also tests on a known db, etc)
- If deployed on the cloud (say within a scheduler like airflow/mlflow), proper dockerization must be set into place (using poetry's dependencies) so that the code works cross-platforms.
- Evaluation could be improved further with other relevant metrics. Specifically a procedure should be chosen for model selection between several models. A dashboard could be built (using a BI tool or fastapi)
- Setting a random seed for result reproductibility would make sense.
- When the model weights are saved, a history should be kept (AWS S3 bucket?) and the code be built in accordance. Predictions as well should be output to a SQL DB or a parquet file in the cloud chosen.
