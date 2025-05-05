# Task

We want to build the family tree of the Rougon-Macquart from textual content of provided [Zola's book](data/La_Fortune_des_Rougon.txt)

## Thought Process

This is detailed in [rundown.md](rundown.md)

## Solution

The different steps of the process are detailed in [rundown.md](./rundown.md), then implemented and simplified in [nb.ipynb](nb.ipynb). They were shortened/combined (because of the time limit of this assessment).
Ideally each step of this notebook would be a dedicated node in a Prefect flow for exemple.

There should also be some level of unit testing for the different steps to make sure they individually perform as planned.

## Install

This was built using uv and dependencies are in [pyproject.toml](pyproject.toml
).

- [Install uv](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)
- run

    ```bash
    uv venv
    source .venv/bin/activate
    uv install
    ```

- run the notebook with the python executable somewhere in .venv

The final [.dot file output by the LLM](data/splits/graphviz_output.dot) is visualized with a [vscode graphviz extension](https://marketplace.visualstudio.com/items/?itemName=tintinweb.graphviz-interactive-preview)

## Run

For now just run [nb.ipynb](nb.ipynb)
