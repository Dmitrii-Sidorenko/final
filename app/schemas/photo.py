from pydantic import BaseModel, ConfigDict, constr
from datetime import datetime
from typing import Optional
class PhotoBase(BaseModel):
    filename: constr(min_length=1)
    filepath: constr(min_length=1)

    model_config = ConfigDict(from_attributes=True)

class PhotoCreate(PhotoBase):
    pass

class PhotoUpdate(BaseModel):
    filename: Optional[constr(min_length=1)] = None
    filepath: Optional[constr(min_length=1)] = None

    model_config = ConfigDict(from_attributes=True)

class PhotoInDBBase(PhotoBase):
    id: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Photo(PhotoInDBBase):
    model_config = ConfigDict(from_attributes=True)