from fastapi import FastAPI

app = FastAPI(
    title="FastAPI Clean Architecture DDD Template",
    summary="Python FastAPI backend template, organized by Clean Architecture layers (domain, application, infrastructure, presentation) and DDD principles. Includes dependency management, Docker support, testing boilerplate, CI-friendly setup and best practices, modular scaffolding to jump-start new projects and ensure long-term maintainability.",
    description="**Your project description goes here. This template is designed to help you build scalable and maintainable applications using FastAPI, following Clean Architecture and Domain-Driven Design principles.**",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Example Tag",
            "description": "Example operations related to a specific feature or module in your application. This tag can be used to group related endpoints together for better organization and clarity.",
        },
    ],
    contact={
        "name": "Bruno Tanabe",
        "url": "https://www.linkedin.com/in/tanabebruno/",
        "email": "tanabebruno@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "identifier": "MIT",
        "url": "https://github.com/BrunoTanabe/microservice-accounts/blob/main/LICENSE",
    },
    terms_of_service="https://github.com/BrunoTanabe/",
    # TODO: Implement default response class, middlewares, exception handlers, and other configurations
    swagger_ui_parameters={
        "displayRequestDuration": True,
        "filter": True,
    },
)
