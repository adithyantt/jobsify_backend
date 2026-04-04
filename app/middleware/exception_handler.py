"""
Global Exception Handler Middleware
"""
import traceback
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("jobsify")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for all unhandled exceptions
    """
    # Log the full traceback
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    
    # Handle different exception types
    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "detail": exc.errors(),
                "message": "Please check your input data"
            }
        )
    
    elif isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Error",
                "detail": exc.detail,
                "message": str(exc.detail)
            }
        )
    
    elif isinstance(exc, SQLAlchemyError):
        logger.error(f"Database error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database Error",
                "detail": "A database error occurred",
                "message": "Please try again later"
            }
        )
    
    elif isinstance(exc, ValueError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Value Error",
                "detail": str(exc),
                "message": "Invalid value provided"
            }
        )
    
    else:
        # Generic error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred",
                "message": "Please try again later"
            }
        )


def create_error_response(status_code: int, message: str, detail: str = None):
    """
    Helper function to create standardized error responses
    """
    content = {
        "error": message,
        "message": message
    }
    if detail:
        content["detail"] = detail
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )
