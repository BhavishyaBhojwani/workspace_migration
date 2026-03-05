"""
Custom exception handling for the API.
Provides consistent error response format similar to Laravel's error responses.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent JSON error responses.
    Similar to Laravel's exception handling format.
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_response = {
            'success': False,
            'message': get_error_message(exc),
            'errors': {},
        }

        # Handle validation errors with field-specific messages
        if hasattr(response, 'data'):
            if isinstance(response.data, dict):
                if 'detail' in response.data:
                    error_response['message'] = str(response.data['detail'])
                else:
                    error_response['errors'] = response.data
                    error_response['message'] = 'Validation failed'
            elif isinstance(response.data, list):
                error_response['message'] = response.data[0] if response.data else 'An error occurred'

        response.data = error_response

    return response


def get_error_message(exc):
    """Extract a human-readable error message from an exception."""
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, str):
            return exc.detail
        if isinstance(exc.detail, dict):
            # Get first error message
            for key, value in exc.detail.items():
                if isinstance(value, list) and value:
                    return str(value[0])
                return str(value)
        if isinstance(exc.detail, list) and exc.detail:
            return str(exc.detail[0])
    return str(exc)


class APIException(Exception):
    """Base API exception for custom error handling."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = 'An error occurred'

    def __init__(self, message=None, errors=None):
        self.message = message or self.default_message
        self.errors = errors or {}
        super().__init__(self.message)

    def to_response(self):
        return Response({
            'success': False,
            'message': self.message,
            'errors': self.errors,
        }, status=self.status_code)


class ValidationException(APIException):
    """Exception for validation errors."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_message = 'Validation failed'


class AuthenticationException(APIException):
    """Exception for authentication failures."""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = 'Authentication failed'


class PermissionDeniedException(APIException):
    """Exception for permission denied errors."""
    status_code = status.HTTP_403_FORBIDDEN
    default_message = 'Permission denied'


class NotFoundException(APIException):
    """Exception for resource not found errors."""
    status_code = status.HTTP_404_NOT_FOUND
    default_message = 'Resource not found'
