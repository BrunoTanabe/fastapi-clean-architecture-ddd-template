from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from starlette.exceptions import HTTPException
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
    debug=settings.ENVIRONMENT_DEBUG,
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=[settings.SECURITY_API_KEY_HEADER],
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
                "name": "example",
                "description": "Example module for demonstrating FastAPI features.",
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

    openapi_schema["components"]["securitySchemes"] = {
        settings.SECURITY_SCHEME_NAME: {
            "type": "apiKey",
            "in": "header",
            "name": settings.SECURITY_API_KEY_HEADER,
            "description": "API Key necessary to access the API endpoints.",
        }
    }

    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation.setdefault("security", []).append(
                {settings.SECURITY_SCHEME_NAME: []}
            )

    app.openapi_schema = openapi_schema
    return openapi_schema


app.openapi = custom_openapi
