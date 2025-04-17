from pydantic import BaseModel
from datetime import datetime

class WeatherBase(BaseModel):
    city: str

class WeatherCreate(WeatherBase):
    temperature: float
    description: str

class WeatherResponse(WeatherCreate):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
