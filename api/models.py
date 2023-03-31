from pydantic import BaseModel

class ImageModel(BaseModel):
    file_name: str | None = None
    url: str

class BlendingRatioModel(BaseModel):
    value: float = 0.0
