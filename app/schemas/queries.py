from pydantic import EmailStr

from app.schemas._core import BaseSchema


class QARequest(BaseSchema):
    query: str


class QAResponse(BaseSchema):
    answer: str | None
    success: bool
