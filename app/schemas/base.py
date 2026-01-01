from pydantic import BaseModel, Field

class BaseSchema(BaseModel):
    context: str = Field(default="https://schema.org", alias="@context")
    type: str = Field(..., alias="@type")