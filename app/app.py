from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware

from fastapi.exceptions import HTTPException
from app.core.exception_handler import (
    validation_exception_handler,
    http_exception_handler,
    internal_exception_handler,
)
from app.core.settings import settings
from app.core.middleware import log_request_middleware, ResponseFormattingMiddleware
from app.core.resources import lifespan
from app.modules.example.presentation.routers import router as example_router
from app.modules.health.presentation.routers import router as health_router

app = FastAPI(
    title=settings.APPLICATION_TITLE,
    debug=settings.APPLICATION_ENVIRONMENT_DEBUG,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "filter": True,
    },
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, internal_exception_handler)


app.add_middleware(BaseHTTPMiddleware, dispatch=log_request_middleware)
app.add_middleware(ResponseFormattingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.SECURITY_BACKEND_ALLOW_ORIGINS],
    allow_credentials=True,
    allow_methods=[str(origin) for origin in settings.SECURITY_BACKEND_ALLOW_METHODS],
    allow_headers=[str(origin) for origin in settings.SECURITY_BACKEND_ALLOW_HEADERS],
)

routers = [
    example_router,
    health_router,
]

for router in routers:
    app.include_router(router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APPLICATION_TITLE,
        summary=settings.APPLICATION_SUMMARY,
        description=settings.APPLICATION_DESCRIPTION,
        version=settings.APPLICATION_VERSION,
        tags=[
            {
                "name": "Example",
                "description": "Example module for demonstrating FastAPI features.",
            },
            {
                "name": "Health",
                "description": "Endpoints for checking the health status of the application.",
            },
        ],
        contact={
            "name": settings.APPLICATION_CONTACT_NAME,
            "url": settings.APPLICATION_CONTACT_URL,
            "email": settings.APPLICATION_CONTACT_EMAIL,
            "phone": settings.APPLICATION_CONTACT_PHONE,
        },
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return openapi_schema


app.openapi = custom_openapi
