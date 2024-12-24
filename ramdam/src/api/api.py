from fastapi import FastAPI

from src.api.data_classes import Payload
from src.model.preprocessing import detect_language

app = FastAPI()


@app.post("/predict_cluster/")
async def predict_cluster(payload: Payload) -> dict[str, str]:
    """Predicts the cluster of the item considered."""
    cluster_name = detect_language(payload.long_description)

    return {"cluster_name": cluster_name}
