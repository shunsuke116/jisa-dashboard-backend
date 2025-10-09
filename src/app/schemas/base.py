from typing import Generic, TypeVar

from pydantic.generics import GenericModel

T = TypeVar("T")


class ResponseModel(GenericModel, Generic[T]):
    result_code: str
    result_msg: str
    result_content: T
