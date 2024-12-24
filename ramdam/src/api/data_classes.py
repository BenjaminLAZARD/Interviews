from pydantic import BaseModel


# Request model
class Payload(BaseModel):
    """Json input for the api."""

    product_name: str
    short_description: str
    long_description: str
