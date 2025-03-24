# Interview

## Problem

The context, as explained [here](https://beavr.notion.site/Beavr-Take-home-interview-backend-12f04bd1285441aeb9fc62c46fd87ac6) is the following:

Create an application to help users manage their policy documents and follow their CSR requirements completion advancement.

### Context

One of the goals of a CSR data management system is to help companies become and stay compliant with official CSR requirements. An example requirement is `Formalized GHG emissions reduction targets and trajectory : The organization has established goals and planned a pathway for reducing GHG emissions over time`.

A company can be considered compliant with a requirement if it has produced the corresponding documents proving the compliance. These documents can be company policies, certificates, company records, etc. For example, in order to be compliant with the previous requirement, a company must have built a GHG policy that formalizes its commitments and targets relating to the management of GHG emissions.

Finally, each document can have several versions (typically one per year), as a document always has an expiration date.

Documents must be validated (typically by the CSR manager of the company) before they are sent to regulatory authorities to be examined.

You are provided with example data of some official CSR requirements and the corresponding documents.

### Data

Check out attached [spreadsheet](./samples/sample_data.xlsx)

### Objectives

The goal is to create an app prototype that would help a company’s CSR manager track and manage the advancement of the company’s requirements compliance.

The app prototype should have the following characteristics :

**Step 1** : When it is started or built, the app should initialize an SQL database with the data in the provided excel spreadsheet. No need to have a UI for that. No need to build a connector to google sheets, feel free to manually download the data in a csv or any other format.

**Step2** : The app should provide a minimalistic frontend with 2 pages :

- A `requirements` page that shows all requirements and their status
- A `documents`  page that shows all documents and their status. This page allows to create a new document version, delete a document version, as well as to update the status.

By prototype, we mean:

- something usable, yet as simple as possible
- UI / design is not important
- we do not expect features which are outside the basic scope of the problem

We expect to use this prototype as a starting point to discuss current implementation details, as well as ideas for improvement.

## Running

### Local Development

- Install poetry in a dedicated environment (pipx?)
- Run `poetry install` (I chose to have a dedicated python environment in a [venv within the project](https://python-poetry.org/docs/configuration/#virtualenvsin-project))
- run `poetry run main.py`

### Running in a Docker container

- `docker build -t app .`
- `docker run -d -p 8000:8000 app`
- On your local machine visit http://localhost:8000/requirements

And when you're done
- `docker stop <container_id>` (or through the desktop app)

## Developing

- Unit tests are under tests
- linting is currently done with ruff (as mentioned in pyproject.toml). Config for the editor is attached within .vscode/settings.

## Roadmap

- build unit tests
- separate javascript, csss from the html (create a static folder under app with style.css and scripts.js)
- improve pydantic validation in schemas.py
