# Browser image search results' quality classification

## Problem

Refer to [LTR_Test_Task.pdf](LTR_Test_Task.pdf)

## Structure of the solution

Please refer to [main.ipynb](main.ipynb) for a detailed explanation of the solution.

## Structure of the repository

Python environment can be installed through anaconda or poetry. [environment.yml](environment.yml) is meant to be informative more than practical for a conda install.

- src contains the customized code built to solve the problem at hand. It corresponds mostly to sklearn-transformers-interface compatible preprocessors built to handle text, categorical values and numerical values in the dataset at hand. They are not scalable and generalizable as it was not the goal of the exercise but show good standards of OOP.
- tests contains a partial implementation of pytest-compatible unit-tests.
- a pyproject.toml .vscode for basic IDE configuration of tests and linting are provided. You may need to configure a file [.vscode/.env](.vscode/.env) for vscode IDE test extension to correctly detect your tests with the single liner `PYTHONPATH="<path-to-the-repo-on-your-machine>"`
