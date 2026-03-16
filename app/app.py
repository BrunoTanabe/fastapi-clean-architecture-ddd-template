from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exception_handler import (
    validation_exception_handler,
    http_exception_handler,
    internal_exception_handler,
)
from app.core.middleware import (
    log_request_middleware,
    ResponseFormattingMiddleware,
    DeviceIdMiddleware,
)
from app.core.resources import lifespan
from app.core.settings import settings
from app.modules.example.presentation.routers import router as example_router
from app.modules.shared.application.enums import ApplicationEnvironment

from app.modules.health.presentation.routers import router as health_router
from app.modules.authentication.presentation.routers import (
    router as authentication_router,
)
from app.modules.user.presentation.routers import router as user_router

# APPLICATION
app = FastAPI(
    title=settings.APPLICATION_TITLE,
    debug=settings.APPLICATION_ENVIRONMENT_DEBUG,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "filter": True,
    },
    lifespan=lifespan,
)


# STATIC FILES
# app.mount("/static", StaticFiles(directory="app/static"), name="static")


# EXCEPTION HANDLERS
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, internal_exception_handler)


# MIDDLEWARES
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.SECURITY_ALLOW_ORIGINS],
    allow_credentials=True,
    allow_methods=[str(method) for method in settings.SECURITY_ALLOW_METHODS],
    allow_headers=[str(header) for header in settings.SECURITY_ALLOW_HEADERS],
)
app.add_middleware(ResponseFormattingMiddleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=log_request_middleware)
app.add_middleware(DeviceIdMiddleware)


# ROUTERS
routers = [
    authentication_router,
    example_router,
    health_router,
    user_router,
]


for router in routers:
    app.include_router(router)


# PRODUCTION SETTINGS
if settings.APPLICATION_ENVIRONMENT == ApplicationEnvironment.PRODUCTION.value:
    app.openapi_url = None
    app.docs_url = None
    app.redoc_url = None


# CUSTOM OPENAPI
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
                "name": "Authentication",
                "description": "Endpoints for user authentication and authorization.",
            },
            {
                "name": "Example",
                "description": "Example module for demonstrating application features.",
            },
            {
                "name": "Health",
                "description": "Endpoints for monitoring the health of the application.",
            },
            {
                "name": "User",
                "description": "Endpoints for managing user resources.",
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
        settings.AUTH_BEARER_TOKEN_SCHEME_NAME: {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        },
        settings.AUTH_API_KEY_SCHEME_NAME: {
            "type": "apiKey",
            "in": "header",
            "name": settings.AUTH_API_KEY_HEADER,
            "description": "API Key necessary to access the API endpoints.",
        },
    }

    app.openapi_schema = openapi_schema
    return openapi_schema


app.openapi = custom_openapi
