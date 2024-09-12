from rest_framework.response import Response
from rest_framework import status


def dispatch_response(data=[], msg = "", status = status.HTTP_200_OK):
    return Response({
        'msg': msg,
        'response': data
    }, status=status)
        

