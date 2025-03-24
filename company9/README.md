# Trial

## Context of the exercise

In this repository we want to use Chat-GPT 3.5 in order to be able to answer some questions on the transcript of a videocall conference, as part of a recruitment interview.

## Install and Run notes

- The project uses [poetry](https://python-poetry.org/) as a package manager. I recommand using miniforge + mamba to install poetry if not already done. All requirement information is then included in the pyproject.toml run `poetry install` in the root directory.
- For repository cleanliness and maintenance, black, flake8 and isort are used.
- In order to store the OpenAI API key, please create a file [config.cfg](./config.cfg) following the example of [config.examplecfg](./config.example.cfg)

- you can just check the alredy executed [cleaned_notebook.ipynb](./cleaned_notebook.ipynb) or run

```cmd
python "src/main.py"
```

(after installing required libraries and ensuring that `python` refers to the appropriate virtual environment).

- For local testing, pytest is used. You can run `python -m pytest tests` from the root directory to check it. For the sake of speed I show only a basic test [test_json.py](./tests/loaders/test_json.py) for the custom jsonloader. It could be more complete and is rather intended as a demo.

## Elements in this repository

- [notebook.ipynb](./notebook.ipynb) shows the actual process that led to a technical solution. Disregard it at first as it is very raw.
- [cleaned_notebook.ipynb](./cleaned_notebook.ipynb) shows the step by step techniques used to solve the problems with every reflection step in markdown. This is where I explain the strategy used and various questions asked...
- [.vscode](.vscode/settings.json) folder contains a basic example on how to configure a local tet editor to adapt to a python env (paths, pytest, file ignored, etc)

There could be a git configuration as well, a makefile to run black, flake8 and isort, etc
