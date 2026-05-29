from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_detail = response.data

        if isinstance(error_detail, dict):
            errors = error_detail
            if 'detail' in errors:
                message = str(errors['detail'])
                errors = {}
            else:
                message = "Erro de validação."
        elif isinstance(error_detail, list):
            message = " ".join(str(e) for e in error_detail)
            errors = {}
        else:
            message = str(error_detail)
            errors = {}

        response.data = {
            "success": False,
            "message": message,
            "errors": errors,
        }

    return response
