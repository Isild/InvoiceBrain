from rest_framework import status
from rest_framework.response import Response


def generate_exception_response(
    data: dict = None, response_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
):
    if data is None:
        data = {"message": "Internal Server Error"}

    return Response(data=data, status=response_code)
