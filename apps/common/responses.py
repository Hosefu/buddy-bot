"""
Стандартизированные API ответы
"""
from rest_framework.response import Response
from rest_framework import status
from typing import Any, Optional, Dict


class APIResponse:
    """Стандартизированные API ответы"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK,
        meta: Optional[Dict] = None
    ) -> Response:
        """Успешный ответ"""
        response_data = {
            "success": True,
            "message": message,
            "data": data
        }
        if meta:
            response_data["meta"] = meta
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(
        message: str,
        error_code: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict] = None
    ) -> Response:
        """Ответ с ошибкой"""
        response_data = {
            "success": False,
            "message": message,
            "error_code": error_code
        }
        if details:
            response_data["details"] = details
        return Response(response_data, status=status_code) 