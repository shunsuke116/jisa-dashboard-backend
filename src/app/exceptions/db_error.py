from urllib.request import Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import status

from src.app.schemas.base import ResponseModel


class SqlExecutionException(Exception):
    pass


def dbaccess_exception_handler(request: Request, exc: SqlExecutionException):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(ResponseModel(result_code="E501", result_msg="データベースアクセスエラー")),
    )
