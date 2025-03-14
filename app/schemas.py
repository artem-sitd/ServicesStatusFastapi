from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class ServiceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = None
    name: str
    description: str


class ServiceStatusUpdate(BaseModel):
    status: str


class ServiceStatusSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = None
    service_id: int
    status: str
    timestamp: datetime


class SlaInputSchema(BaseModel):
    name: str
    start_time: str
    end_time: str

    @field_validator("start_time", "end_time")
    def validate_date(cls, v):
        try:
            return datetime.strptime(v, "%d-%m-%Y")
        except ValueError:
            raise ValueError("Incorrect date format, should be DD-MM-YYYY")
