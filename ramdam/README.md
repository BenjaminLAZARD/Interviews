# RAMDAM exercises

[Description of the problem](https://hello-ramdam.notion.site/Case-Study-Founding-AI-ML-Engineer-14cd54f28d1c80df9905c3c934f1e4bc)

## Exercise 1

A simple solution for clustering using TFIDF is coded within the src folder. The steps that led to that solution, another solution using sentence-embedding and a conclusion on the matter are detailed in notebook test.ipynb.

Since the clustering algorithm was not very convincing as a first approach, and because of the limited time allocated to the task, instead of implementing the conclusion suggested in the notebook, The API part will just return the language of the query for now. Ideally, I would create the solution described in the conclusion of the notebook.

Ideally I would provide a docker image to reproduce the setup. For lack of time, I am providing a way of testing the API locally:

- run `uvicorn src.api.api:app`from the root of this project
- when the server is up, navigate to <http://127.0.0.1:8000/docs>
- Navigate to a web-browser console and type in the following query:
```js
fetch("http://127.0.0.1:8000/predict_cluster/", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        "product_name": "My product",
        "short_description": "lorem",
        "long_description": "Essayons de voir si la detection de langage fonctionne"
    })
})
.then(response => response.json())
.then(data => console.log("Response:", data))
.catch(error => console.error("Error:", error));
```
The console should load "{cluster_name: 'fr'}"

Regarding the prediction lifecycle, I believe, I would use a periodic workflow when I rerun clustering on the last X months campaigns.
We can monitor the performance of the current clustering algorithm on new data by using silhouette detection and measuring the % of items marked as noise (cluster -1).

The algorithm I used (HDBSCAN) also supports incremental clustering (does not need to be retrained with data it is already trained on), to allow for continuous learning.
Platform would likely be airflow with docker images hosted on AWS.

## Exercise 2