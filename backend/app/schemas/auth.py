from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import UserRole


class LoginRequest(BaseModel):
    username_or_email: str = Field(min_length=1)
    password: str = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def normalize_identifier(cls, values: Any) -> Any:
        if isinstance(values, dict) and "username_or_email" not in values:
            values = dict(values)
            values["username_or_email"] = values.get("username") or values.get("email")
        return values


class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
