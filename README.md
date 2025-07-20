# FastAPI Clean Architecture and Domain-Driven Design Template

The **fastapi-clean-architecture-ddd-template** repository is a Python backend project template, aimed at applications that use FastAPI and potentially Artificial Intelligence components. This project serves as a foundation for creating new applications following a modular and scalable architecture, promoting separation of concerns and ease of maintenance. The architecture adopted is inspired by **Clean Architecture** and **Domain-Driven Design (DDD)** principles, organizing the code into well-defined layers: domain, application, infrastructure, and presentation, along with core configuration components.

This README documents the project's structure, explaining the purpose of each folder and file, naming conventions, dependencies used, and best practices to follow. In the end, any team member should be able to understand the proposed architecture and know how to extend the template for new features without doubts.

## Table of Contents

* [Architecture Overview](#architecture-overview)
* [Folder and File Structure](#folder-and-file-structure)

  * [Project Root](#project-root)
  * [`app/` Directory (Application)](#app-directory-application)

    * [`app/core/` Directory (Core Configuration)](#appcore-directory-core-configuration)
    * [`app/modules/` Directory (Feature Modules)](#appmodules-directory-feature-modules)

      * [Example Module: `app/modules/example/`](#example-module-appmodulesexample)

        * [Domain](#domain)
        * [Application](#application)
        * [Infrastructure](#infrastructure)
        * [Presentation](#presentation)
  * [`docs/` Directory (Documents)](#docs-directory-documents)
  * [`scripts/` Directory (Utility Scripts)](#scripts-directory-utility-scripts)
  * [`test/` Directory (Tests)](#test-directory-tests)
* [Implementation Guide and Best Practices](#implementation-guide-and-best-practices)

  * [Separation of Concerns and Layers](#separation-of-concerns-and-layers)
  * [File and Code Naming Conventions](#file-and-code-naming-conventions)
  * [Dependency Inversion and Dependency Injection](#dependency-inversion-and-dependency-injection)
  * [Code Standards and Quality](#code-standards-and-quality)
  * [Test Structure](#test-structure)
* [Project Dependencies](#project-dependencies)
* [Environment Setup and Execution](#environment-setup-and-execution)

  * [UV Package Manager](#uv-package-manager)
  * [Setting Environment Variables (.env)](#setting-environment-variables-env)
  * [Installing Dependencies](#installing-dependencies)
  * [Running the Application](#running-the-application)
  * [Using Docker (Optional)](#using-docker-optional)
* [Final Considerations](#final-considerations)

## Architecture Overview

The **fastapi-clean-architecture-ddd-template** architecture is structured to clearly separate the responsibilities of each part of the application, in a manner similar to Clean Architecture. This means that **business rules and domain logic** are isolated from infrastructure details or external interfaces. At a high level, we adopt the following layers:

* **Domain:** Contains business entities, pure business rules, value objects, and domain services. This layer is independent of any external framework or implementation detail. It represents the core of the application (the reason the software exists) and should have no external dependencies.
* **Application:** Implements the application's **use cases**. It orchestrates domain operations, coordinating data between the input interface (e.g., the API) and the domain. This layer also defines **interfaces (ports)** that the domain/application expects to perform certain tasks (e.g., data repositories). The Application layer depends only on the Domain layer (e.g., knows about entities and repository interfaces) and is unaware of infrastructure details.
* **Infrastructure:** Provides concrete implementations for the interfaces defined in the Application (or Domain) layer. This includes details such as database access, external API calls, ORM database models, email sending, AI service integration, etc. The Infrastructure layer **depends** on the Domain and Application layers (e.g., imports entities or interfaces to implement repositories), but not the other way around. This layer handles *how* things are persisted or communicated externally.
* **Presentation:** Also called the interface or user interface layer. In the context of a web API, this is where **FastAPI controllers** or **routers**, **schemas** (Pydantic models) for API input and output, and request **dependencies** (like repository injection, authentication, etc.) are defined. This layer receives user requests (HTTP), validates data, invokes the appropriate use cases in the Application layer, and returns the HTTP response. It depends on the Application and Domain layers (e.g., uses use cases, domain schemas), but should not contain business logic.

In addition to these main layers, the project has a **Core Configuration** for cross-cutting concerns (such as settings, database connections, logging, common security, etc.), and supporting structures for documentation, development scripts, and tests.

This separation brings several benefits:

* **Maintainability:** Changes in business rules (domain) do not affect external details and vice versa. Each concern is isolated.
* **Testability:** Business logic can be tested in isolation by mocking or stubbing infrastructure dependencies via interfaces.
* **Flexibility and Extensibility:** Infrastructure implementations (e.g., switching the database or AI provider) can be changed without refactoring business logic, by simply providing a new implementation of the expected interface.
* **Feature-Based Organization:** The `app/modules` folder allows grouping code related to a specific business context (module) in one place, rather than in globally separated layers. Each module contains its own sub-layers (domain, application, etc.), making it easier to find everything related to that feature.

In summary, the proposed architecture follows the principle of **dependency inversion**: inner layers know nothing about outer layers, and system dependencies always point from outer to inner layers (Presentation → Application → Domain, and Infrastructure → Domain/Application). Below, we detail the entire folder and file structure of the project and the role of each.

## Folder and File Structure

The following is the directory and file structure of the project, as found in the repository:

```text
fastapi-clean-architecture-ddd-template
├── .env
├── .env.example
├── .git/
├── .gitignore
├── .python-version
├── .venv/
├── Dockerfile
├── LICENSE
├── README-PTBR.md
├── README.md
├── app
│   ├── __init__.py
│   ├── app.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── exception_handler.py
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   ├── middleware.py
│   │   ├── resources.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   ├── settings.py
│   │   └── utils.py
│   └── modules
│       ├── __init__.py
│       └── example
│           ├── __init__.py
│           ├── application
│           │   ├── __init__.py
│           │   ├── interfaces.py
│           │   ├── use_cases.py
│           │   └── utils.py
│           ├── domain
│           │   ├── __init__.py
│           │   ├── entities.py
│           │   ├── mappers.py
│           │   ├── services.py
│           │   └── value_objects.py
│           ├── infrastructure
│           │   ├── __init__.py
│           │   ├── models.py
│           │   └── repositories.py
│           └── presentation
│               ├── __init__.py
│               ├── dependencies.py
│               ├── docs.py
│               ├── exceptions.py
│               ├── routers.py
│               └── schemas.py
├── docker-compose.yaml
├── docs/
├── pyproject.toml
├── requirements.txt
├── scripts
│   ├── __init__.py
│   └── directory_tree.py
├── test
│   ├── __init__.py
│   ├── core
│   │   └── __init__.py
│   └── modules
│       ├── __init__.py
│       └── example
│           └── __init__.py
└── uv.lock
```

Next, we explain each part of this structure in detail:

### Project Root

At the root of the repository are configuration files, environment files, and general project documentation:

* **.env:** Environment variable file (not versioned) that stores sensitive or environment-specific settings (e.g., credentials, database URLs, API key configs). This file is read by the application (via `pydantic-settings`) to configure runtime parameters. Each developer can have their own local `.env` with settings appropriate for their environment.
* **.env.example:** Sample environment file, containing only expected variable names and example or empty values. Serves as documentation for what variables need to be defined in the actual `.env` file, without exposing sensitive data. Best practice is to copy this file to `.env` and fill in the necessary values.
* **.gitignore:** List of file and folder patterns Git should ignore (not version). Usually includes `*.env`, virtual environment files (`.venv/`), cache files, build artifacts, etc., to avoid committing sensitive or irrelevant files.
* **.git/**: Git’s internal directory containing all repository history and configuration. *(You don’t manually interact with this folder; Git manages it.)*
* **.python-version:** File specifying the Python version used by the project (e.g., `3.13.x`). This can be used by tools like **pyenv** or the **uv** manager to automatically activate the correct Python version when entering the project directory. It ensures the project runs with the proper Python version.
* **.venv/**: Virtual environment directory where Python project dependencies are installed locally. This is created and managed by the **uv** package manager (or other tools). It contains the Python binaries and all packages installed for the project, isolated from the global system. This directory is ignored by Git.
* **Dockerfile:** Configuration file for **Docker** that defines how to build a container image of the application. It specifies the base image (typically Python), copies project files, installs dependencies (using `pyproject.toml`/`uv.lock`), and sets the startup command (usually running a Uvicorn server for the FastAPI app). With the Dockerfile, a backend container image can be created, facilitating deployment in standardized environments.
* **docker-compose.yaml:** Configuration file for **Docker Compose** describing how to run multi-service containers. In this project, `docker-compose.yaml` can orchestrate the application container (defined by the Dockerfile) along with other services the backend may require, such as a database or cache. For example, a PostgreSQL or Redis service can be configured here for development. This file simplifies spinning up the entire dev/production environment with a single command.
* **README.md:** Project documentation (this file). Contains architectural explanations, usage instructions, etc., serving as a guide for developers using or maintaining the template.
* **requirements.txt:** List of project dependencies. Used to install project dependencies in environments that do not support `pyproject.toml` directly (e.g., some servers or tools). It contains the exact versions of installed packages, allowing reproducibility. However, the preferred approach is to use `pyproject.toml` with the **uv** manager.
* **pyproject.toml:** Project configuration file, following the [PEP 621](https://peps.python.org/pep-0621/) standard and used by the **uv** package manager (and also supported by build tools like Poetry, etc.). This file defines:

  * Project metadata (name, version, description).
  * Project dependencies (required libraries like FastAPI, Pydantic, etc.).
  * Optional dependency groups, e.g., `dev` for development dependencies (in this project, the Ruff linter is listed here).
  * README file as the main document.
  * Minimum required Python version.

  The `pyproject.toml` replaces the old `requirements.txt` and setup.py, centralizing package/project information. **Important:** Exact versions of each dependency are not usually specified here (only minimums or ranges); exact version control is handled by the lock file (`uv.lock`).
* **uv.lock:** Lock file automatically managed by **uv**. It lists **all** installed dependencies (including transitive dependencies) with exact versions and hashes, ensuring environment reproducibility. You **should not edit** this file manually; it’s updated via `uv` commands (like `uv sync` or `uv lock`). The `uv.lock` file should be committed so that other developers get the same package versions when syncing the project.

### `app/` Directory (Application)

The `app/` directory contains all of the application’s **Python** source code. It is a Python package (note the `__init__.py` file inside) and houses both the FastAPI application instance and the sub-modules organized by functional domain. In larger projects we might have multiple application packages, but here we use a single `app` package to gather everything in the backend.

Main components inside `app/`:

* **`app.py`:** The main FastAPI application file—the backend **entry point**. Inside it we typically instantiate the FastAPI app and include the routes defined in the various modules. For example:

  * Creates the object `app = FastAPI(...)`, configuring title, version, etc.
  * Loads initial settings (e.g., setting log level from `core/logging.py`, or reading configs from `core/config.py`).
  * Includes each module’s routers using `app.include_router(...)`, registering the routes from the different parts of the API. In our case it will include the router from the example module (and, in the future, from other modules).
  * Defines startup or shutdown event handlers if needed (e.g., a `startup` function to connect to the database via `core/database.py`, or `shutdown` to close connections).

  In short, `app.py` assembles the application by composing pieces defined elsewhere. This file (more precisely, the `app` object in it) is what you point to when running the server.

* **`__init__.py`:** An empty (or nearly empty) file whose only purpose is to mark `app` as a Python package. There’s no need to put logic here, though you could use it to set up global imports if desired (keeping it empty for simplicity is fine).

#### `app/core/` Directory (Central Configuration)

The `app/core` package contains foundational configuration modules and utilities for the application. These are low-level or cross-cutting components that are usually used by multiple parts of the system. Details of the files inside `core/`:

* **`core/database.py`:** Module responsible for setting up the database connection or other persistent data resources. For example, if we use SQLAlchemy, this is where we might instantiate the connection engine using the DB URL from the settings (`settings.database_url`), create a sessionmaker, and provide utility functions to obtain a session (to be used as a FastAPI dependency). If we don’t use a relational DB, this module could configure a NoSQL connection, or—if the app is AI-focused—manage a vector store, etc. In short, it’s the central point for initializing and sharing data connections. For example:

  ```python
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker
  from app.core.settings import settings

  engine = create_engine(settings.database_url)
  SessionLocal = sessionmaker(bind=engine)

  def get_db():
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()
  ```

  In contexts without a database this file may remain minimal or empty, but it’s ready to integrate persistence cleanly.

* **`core/exception_handler.py`:** Defines global exception handlers for the application. Here we can configure how FastAPI should handle unhandled errors, converting specific exceptions into appropriate HTTP responses. For instance, we can catch validation exceptions and return 422 errors, or convert DB errors into 500s. This centralizes error handling and ensures all parts of the app follow a consistent pattern. A simple example:

  ```python
  from fastapi import Request, HTTPException
  from fastapi.responses import JSONResponse

  async def http_exception_handler(request: Request, exc: HTTPException):
      return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
  ```

  In `app.py`, we register this handler with `app.add_exception_handler(HTTPException, http_exception_handler)`.

* **`core/exceptions.py`:** Defines a base class to be inherited by custom application exceptions (usually inheriting from `Exception` or `BaseException`). These custom exceptions can represent domain-specific or business-logic errors, allowing us to treat those cases differently. For example, we might have a `DomainError` exception raised when a business rule fails, which the global handler converts into a suitable HTTP error.

  ```python
  class DomainError(Exception):
      """Base exception for domain errors."""
      pass
  ```

* **`core/logging.py`:** Sets up the application’s global **logging** configuration. Before the server starts we want to configure how logs will be formatted and what detail level will be shown (info, debug, error, etc.). This file uses Python’s built-in `logging` module to configure handlers, formatters, and levels. For example, we can define a unified log format or integrate the `loguru` library if preferred. At app startup (`app.py`), we call the logging setup function. A possible content:

  ```python
  import logging

  LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

  def setup_logging():
      logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
      # ... additional settings if needed
  ```

  This way, when the application starts we call `setup_logging()` and ensure well-formatted logs at the correct level. A solid log configuration is crucial for debugging and production monitoring.

* **`core/middleware.py`:** Defines global middlewares for the application. Middlewares are functions that intercept requests and responses, allowing you to add common behaviors such as authentication, request logging, CORS handling, etc. In this file we can define middlewares applied to every route. For example, a middleware to log each received request and its response:

  ```python
  from fastapi import Request
  from starlette.middleware.base import BaseHTTPMiddleware

  class LoggingMiddleware(BaseHTTPMiddleware):
      async def dispatch(self, request: Request, call_next):
          response = await call_next(request)
          # Here you can log request/response details
          return response
  ```

  In `app.py`, we register this middleware with `app.add_middleware(LoggingMiddleware)`.

* **`core/resources.py`:** Module for managing static resources or configuration files the application may need. For example, if the app uses HTML templates, static files (CSS, JS), or additional config files, we can define functions here to load those resources. This centralizes access to non-code files required by the app. It can also initialize and tear down resources like external service connections (e.g., third-party APIs) that aren’t databases.

* **`core/schemas.py`:** Defines **Pydantic schemas** inherited by other parts of the app. Schemas are used for validating input and output data, especially in APIs. Here we can define common schemas reused across multiple modules, such as `BaseResponse`, `ErrorResponse`, or other generics that don’t belong to a specific module. For example:

  ```python
  from pydantic import BaseModel

  class BaseResponse(BaseModel):
      success: bool
      message: str | None = None
  ```

  These schemas can be imported and used in different modules to ensure consistency in response structure.

* **`core/security.py`:** Module for **shared security** functionality. For example, utilities for password hashing, JWT generation and verification, CORS policies, authentication contexts, etc. The idea is to centralize security aspects used in multiple modules.

  * If the app requires user authentication, this file might include functions to create/verify JWT tokens (e.g., with `python-jose`), functions to hash/verify passwords (e.g., with `passlib`).
  * It can also define OAuth credentials or authorization scopes.

  **Note:** Route-specific auth/authorization may be configured in the *routers* (presentation layer), but generic support functions (like verifying a token signature, fetching the current user from the token, etc.) can live here in core. This avoids repetition and ensures the same security utilities are used throughout the project.

In summary, `app/core/` hosts code that is cross-cutting and domain-agnostic, forming the foundation of the entire application.

* **`core/settings.py`:** Application **configuration** module. Here we define classes and objects that load environment variables (e.g., using `pydantic_settings.BaseSettings`). In a typical FastAPI project this file defines a `Settings` class with attributes for every needed configuration (e.g., `APP_NAME`, `DEBUG`, `DATABASE_URL`, API credentials, etc.). The `Settings` class loads values from the `.env` file by default. A simplified example:

  ```python
  from pydantic_settings import BaseSettings

  class Settings(BaseSettings):
      app_name: str = "FastAPI Clean Architecture DDD Template"
      debug: bool = False
      database_url: str  # etc., other config fields...
      class Config:
          env_file = ".env"

  settings = Settings()
  ```

  Other parts of the code then import `settings` to access configurations (e.g., `settings.database_url`). This pattern centralizes all configs in one place and lets you change behavior via environment variables without altering code. Remember to keep secrets (e.g., secret keys) only in the .env and not commit them.

* **`core/utils.py`:** Module for general utility functions that don’t fit elsewhere. Here we can place helper functions used in multiple places within `core`, such as string formatting, date manipulation, generic validations, etc. The goal is to avoid code duplication and centralize simple logic that can be reused.

#### `app/modules/` Directory (Feature Modules)

This directory is where we organize code by **feature or domain context**. Each sub-folder inside `modules` represents a **module** or **bounded context** of the application, encapsulating domain logic, use cases, interfaces, and infrastructure details related to that functionality.

For example, we might have modules like `users`, `orders`, `payments`, `recommendation`, etc., each containing its entities, use cases, repositories, routes, etc. In our template we have an example module called **`example/`** that demonstrates the structure. New modules to be created in the future should follow the same internal organization pattern.

Structure of a typical module (using the `example` module as a model):

##### Example Module: `app/modules/example/`

The **example** module was generated as a reference and starting point. It implements the suggested architecture within a fictional “example” domain. Inside it there are sub-folders for each logical layer of the module:

* **application/** – Application layer (use cases and interfaces).
* **domain/** – Domain layer (entities and business logic).
* **infrastructure/** – Infrastructure layer (persistence details, external APIs, etc.).
* **presentation/** – Presentation layer (FastAPI endpoints, request/response schemas, dependency injection).

Each sub-folder contains specific files as described below:

###### Domain

This sub-folder defines the core business rules of the module. The files here describe **what** the principal domain concepts are and how they behave, with no dependency on external details (database, FastAPI, etc.).

* **`entities.py`:** Defines the module’s **Domain Entities**. Entities are classes or structures representing the fundamental business objects the module deals with, including their attributes and possibly basic internal logic. For example, in a user module we could have a `User` entity with id, name, email, and methods to verify a password or change a profile. Entities should encapsulate invariants and simple rules related to themselves.

  In Python, entities can be implemented as normal classes or even dataclasses, depending on need. The important thing is that they don’t depend on how they are stored or displayed—they are purely business models. In an AI context, if this module involved something like a “Model” or “Dataset,” those could be entities as well (representing configuration or state of those objects).

* **`mappers.py`:** This file contains functions or classes that convert domain entities to formats suitable for persistence (such as ORM models) and vice versa. For instance, if we’re using SQLAlchemy, here we could have functions that transform a `User` entity into a `UserModel` SQLAlchemy model and another function that does the reverse. This keeps entities pure and decoupled from persistence details.

  Mappers are useful to keep conversion logic centralized, avoiding code duplication in repositories or services. If the module doesn’t require complex mapping, this file can be omitted or stay empty.

* **`value_objects.py`:** Contains definitions of types or classes that represent domain values with their own logic or invariants but no unique identity like entities. In Domain-Driven Design, **Value Objects** are immutable and compared by value, not by identity.

  Common examples: a CPF, an Email, a monetary amount, coordinates, etc., which you might represent with their own class to enforce formatting or validation. In this file you can define classes for such specific values, encapsulating checks (e.g., an `Email` class that validates format in the constructor). In the example module we might have something like a `Score` or another demonstrative VO.

  Keeping value objects separate helps make the code more expressive and ensures domain data integrity. If your domain doesn’t have complex value objects, this file can remain empty or be omitted, but the structure is ready if needed.

* **`services.py`:** This file gathers **complex domain logic** that doesn’t fit within a single entity or concerns interaction between multiple entities. Domain Services are functions or classes implementing business rules using entities and value objects, but that don’t belong exclusively to any specific entity.

  For example, in a financial domain we might have a domain service to calculate interest or validate a transaction between two accounts (involving two `Account` entities). In an AI context there could be a domain service to run an inference pipeline or combine results from multiple models, if that is considered part of the domain rather than mere infra.

  These domain services **should still not access infrastructure**. They operate on domain objects loaded into memory (probably by repositories) and apply pure logic to them. If they need data from outside or must save results, they should receive that data via parameters or return results for higher layers (application) to persist.

  In short, put in `services.py` business rules involving more elaborate logic or multiple objects, keeping entity code lean.

###### Application

The `application` sub-folder implements the module’s **use cases** and defines **interfaces (ports)** that connect the application layer with other layers. This layer orchestrates the actions required to fulfill operations requested from the outside world (e.g., an API endpoint), coordinating entities, calling domain services, and using repositories (interfaces).

* **`interfaces.py`:** Defines the **abstract interfaces** or contracts that the application layer expects to perform certain infrastructure tasks. Typically the main interfaces here are the domain **Repositories**.

  For example, if the `example` domain needs to read and write objects from a database, here we define an abstract repository interface (e.g., `class ExampleRepositoryInterface(ABC): ...`) with methods like `list_objects()`, `get_by_id(id)`, `save(obj)`, etc. These interfaces can be abstract classes using `abc.ABC` and `@abstractmethod` or Python 3.8+ **protocols** (`typing.Protocol`) describing the expected methods. The domain/application then depends on this interface, without knowing which concrete implementation will be used.

  Besides repositories, we can define interfaces for other external services the application uses, e.g., an email service interface, an AI provider interface (if you want to abstract calls to external models), etc. Anything the application logic needs to call but which is an infrastructure detail can be formalized as an interface here.

  By isolating interfaces here we apply the **Dependency Inversion** principle: the application layer defines the contract, and the concrete implementation comes from infrastructure (inverting the dependency). This lets us easily swap implementations (e.g., use an in-memory repository for tests and a real SQL repository in production, both fulfilling the same interface).

* **`use_cases.py`:** Contains the implementation of the module’s **Use Cases**. Each use case represents a specific action or functionality the system provides, aggregating the logic needed to accomplish it.

  Use cases can be implemented in different ways:

  * As simple **functions** when the logic is small.
  * As **classes** (e.g., one class per use case with an `execute()` method, or making the class callable via `__call__`). The class approach is handy if the use case needs to inject a repository via the constructor and then execute.

  For example, suppose the example module manages “foo.” We might have a `CreateFoo` and a `ListFoo` use case. In code we could have:

  ```python
  from app.modules.example.domain.entities import Foo
  from app.modules.example.application.interfaces import FooRepositoryInterface

  class FooUseCase:
      def __init__(self, repo: FooRepositoryInterface):
          self.repo = repo
      
      def create_foo(self, data: dict) -> Foo:
          # Validate and create entity
          foo = Foo(**data)
          # Business rules (call domain services if needed)
          # ...
          # Persist using the repository
          saved_foo = self.repo.save(foo)
          return saved_foo

      def list_foos(self) -> list[Foo]:
          # Get all Foos from the repository
          return self.repo.list()
  ```

  In this example the `FooUseCase` receives a repository implementation via injection (in the constructor) and uses it to store the created entity. It coordinates entity creation and rule application. The same style applies to read use cases: obtain data from the repo, possibly apply some rule (e.g., filter, sort, calculate something), and return the result.

  The important point is that **Use Cases know nothing about HTTP, JSON, or API details**—that’s handled in the presentation layer. They receive and return domain objects (or plain Python structures) and can raise business exceptions if something prevents execution (e.g., “Foo already exists,” “Invalid data,” etc.), which the presentation layer will transform into appropriate HTTP responses.

  We can implement multiple use cases in `use_cases.py`. If the file gets too large, a good practice is to split by functionality (e.g., one file per complex use case, or grouping related ones). But the template initially leaves a single file for simplicity.

* **`utils.py`:** Contains utility functions specific to the application layer. Here we can place helper functions used by multiple use cases, such as common validations, data formatting, etc. The goal is to avoid duplication and centralize simple logic reusable across different use cases.

  For example, if several use cases need to validate input formats (like checking whether an email is valid), we can have a function `validate_email(email: str) -> bool` here. The use cases can then call this function instead of duplicating the logic.

###### Infrastructure

The module’s `infrastructure` sub-folder contains the concrete implementations of the technology details required by the module, fulfilling the interfaces defined in the application layer. Here we deal with persistence, external calls, and anything involving external resources or framework details.

* **`models.py`:** Defines the **infrastructure data models**, typically database models or ORM mappings. For example, if we use **SQLAlchemy**, this file can declare SQLAlchemy model classes corresponding to the domain entities, with their tables, columns, and relationships. Sometimes the domain entities may coincide structurally with the DB models, but that isn’t required—we may have differences (e.g., technical fields in the DB model that don’t exist in the entity, or vice versa).

  Example (using SQLAlchemy ORM):

  ```python
  from sqlalchemy import Column, Integer, String
  from app.core.database import Base

  class FooModel(Base):
      __tablename__ = "foo"
      id = Column(Integer, primary_key=True, index=True)
      name = Column(String, index=True)
      description = Column(String)
      # etc...
  ```

  Where `Base` would be the declarative base class imported from `core/database.py`. Repositories use these models to perform CRUD operations. If you use another kind of persistence (e.g., an ODM for Mongo, or direct access via client libraries) you might not have a formal “models.py,” but you will still have infrastructure-specific data representations here (e.g., Mongo schemas or JSON document mappings).

  In AI scenarios, `models.py` could contain classes to interact with a pre-trained ML model or endpoint, but usually that would be more of a service than a data model. In that case you could create infrastructure classes to encapsulate calls to external AI models (e.g., the OpenAI API)—those classes could reside here or in `repositories.py` depending on how you categorize them (are they knowledge repositories or external services? You can treat them similarly).

* **`repositories.py`:** Contains the **concrete repository implementations** defined in `application/interfaces.py`. Here we write classes (or functions) that access the real data source to retrieve or save information.

  Continuing the Foo example, if `interfaces.py` defines `FooRepositoryInterface` with certain methods, `repositories.py` will have a `FooRepository` class (implementing `FooRepositoryInterface`) that performs the actual operations using the database or other means.

  Example:

  ```python
  from app.modules.example.application.interfaces import FooRepositoryInterface
  from app.modules.example.infrastructure.models import FooModel
  from app.core.database import SessionLocal

  class FooRepository(FooRepositoryInterface):
      def __init__(self, db_session=None):
          self.db = db_session or SessionLocal()

      def list(self) -> list[Foo]:
          results = self.db.query(FooModel).all()
          # Map FooModel (ORM) to Foo entity (domain.entities)
          return [Foo.from_model(m) for m in results]

      def get_by_id(self, id: int) -> Foo | None:
          model = self.db.query(FooModel).get(id)
          return Foo.from_model(model) if model else None

      def save(self, foo: Foo) -> Foo:
          model = FooModel.from_entity(foo)
          self.db.add(model)
          self.db.commit()
          self.db.refresh(model)
          return Foo.from_model(model)
  ```

  *(Note: methods `from_model` and `from_entity` would be helper methods to convert between domain entities and ORM models, which you might implement to keep the domain separate from the ORM layer.)*

  In this example, the repository receives a database session (which we can obtain via `app.core.database.SessionLocal`). In FastAPI we’ll use dependency injection to provide one session per request (see `dependencies.py` in the presentation layer). The repository performs the query or persists data and returns domain objects.

  If the application uses a different database or an external API, this repository could call the appropriate endpoints, parse the response, and transform it into domain entities. For instance, if `example` were a module that fetches data from an external service, the repository might use `httpx` (included via `fastapi[standard]`) to make requests and then build entities.

  **Important:** The repository is part of infrastructure, so it can and should know both infrastructure models (`FooModel`, or external API details) and domain entities (`Foo`). It acts as an adapter converting between the two worlds. The logic here should be limited to data operations (queries, conversions), not business rules (those belong in domain/application).

###### Presentation

The `presentation` sub-folder defines how the module exposes its functionalities to the outside world—here via a web API (FastAPI). It houses the **routers** (controllers) with HTTP endpoints, the **Pydantic schemas** for validation/serialization, and the module-specific **dependencies** (e.g., repository providers or authentication providers for use in the endpoints).

* **`routers.py`:** Defines the API routes (endpoints) for this module. Typically we create a `router = APIRouter()` object and decorate Python functions with HTTP verbs (@router.get, @router.post, etc.) for each needed endpoint.

  Each endpoint function should handle:

  * Receiving validated inputs (path params, query params, body) using the schemas (see below).
  * Obtaining required instances via dependencies (e.g., a repository or the current authenticated user).
  * Calling the appropriate use case in the application layer, passing the necessary data.
  * Handling business exceptions raised by the use cases (e.g., converting a “not found” exception into an HTTP 404, or a validation error into 400).
  * Returning the result (converting to an output schema if it’s a complex object, or simply returning basic types that FastAPI will convert automatically).

  For example, suppose a GET endpoint to list Foos:

  ```python
  from fastapi import APIRouter, Depends, HTTPException
  from app.modules.example.presentation.schemas import FooOut
  from app.modules.example.application.use_cases import ListFoosUseCase
  from app.modules.example.presentation.dependencies import get_foo_repository

  router = APIRouter(prefix="/foo", tags=["Foo"])

  @router.get("/", response_model=list[FooOut])
  def list_foos(repo = Depends(get_foo_repository)):
      use_case = ListFoosUseCase(repo)
      foos = use_case.execute()
      return foos  # FastAPI will convert each Foo via FooOut schema
  ```

  In this pseudo-code:

  * We use `Depends(get_foo_repository)` to inject a concrete repository instance (defined in `infrastructure`) that satisfies the expected interface.
  * We instantiate the `ListFoosUseCase`, providing the repository.
  * We execute and obtain the result (a list of `Foo` entities).
  * We return that list; FastAPI uses the `response_model` `list[FooOut]` to filter and serialize the response as defined in the schema.
  * Error handling: if `execute()` raised an exception we could catch it and raise the corresponding `HTTPException`.

  The `routers.py` file can contain multiple routes (GET, POST, PUT, DELETE) according to the module’s operations. If the routes become numerous, we can split into multiple files (e.g., `routers_public.py`, `routers_admin.py`) and include them all in a main APIRouter, but the template keeps a single file for simplicity.

  Finally, in `app.py`, the example module’s router would be included in the main app:

  ```python
  from app.modules.example.presentation.routers import router as example_router
  app.include_router(example_router)
  ```

  possibly with a prefix (e.g., a global `/api/v1`, or specific prefixes if desired).

* **`docs.py`:** This file is optional and can be used to separate documentation specific to the module, such as endpoint descriptions, usage examples, or additional route details for better code organization when the docs are extensive. However, in many cases endpoint documentation can be done directly in the routes using docstrings and FastAPI annotations, so this file can remain empty or be omitted.

* **`exceptions.py`:** Defines exceptions specific to the module that may be raised by endpoints or use cases. These exceptions can signal domain-specific errors (e.g., “Foo already exists,” “Foo not found”) and can be caught by the global exception handler (`core/exception_handler.py`) to return appropriate HTTP responses.

  For example, we might have:

  ```python
  class FooAlreadyExistsException(Exception):
      """Exception raised when a Foo already exists."""
      pass
  ```

  Then, within use cases or routes, we can raise this exception when needed, and the global handler will turn it into an HTTP 409 Conflict response.

* **`schemas.py`:** Defines the **Pydantic Schemas** used to validate and serialize input and output data for this module’s API endpoints. Pydantic (v2, integrated via FastAPI) allows creation of model classes representing the expected/returned JSON structure, with automatic type validation.

  Typically we’ll have:

  * **Input Schemas**: Represent POST/PUT request bodies or complex parameters. Example: `FooCreate` with required fields to create a Foo.
  * **Output Schemas**: Represent how the entity is exposed through the API. Example: `FooOut` with fields to return to the client (usually matching entity fields, minus secrets or irrelevant ones).

  In FastAPI, we use these schemas in route functions: function parameters for body (e.g., `foo: FooCreate` gets automatically populated and validated) and `response_model=FooOut` for response conversion.

  In the example module, we might have in `schemas.py`:

  ```python
  from pydantic import BaseModel

  class FooBase(BaseModel):
      nome: str
      descricao: str

  class FooCreate(FooBase):
      pass  # Same fields for now, but separated in case of future differences

  class FooOut(FooBase):
      id: int

      class Config:
          from_attributes = True  # Allows creating FooOut from ORM/dataclass with matching attributes
  ```

  Here we define a base schema with shared fields, a creation schema (same as base for now), and an output schema that includes the id. `from_attributes = True` is a Pydantic v2 setting that allows automatic conversion from objects with matching attributes (useful when returning domain entities or ORM models; FastAPI/Pydantic can extract the data).

  Schemas serve as the API contract—they document and validate the expected format. Keep them updated as the domain evolves, but don’t include fields that shouldn’t be exposed (e.g., passwords, secrets, etc.).

* **`dependencies.py`:** Defines FastAPI **dependency functions** specific to the module. These functions use FastAPI’s **Dependency Injection** system (`fastapi.Depends`) to provide ready-to-use objects for endpoints, keeping route code cleaner and decoupled from object creation.

  Common dependencies defined here include:

  * **Repository or service instantiation**: e.g., `def get_foo_repository():` that instantiates and returns a `FooRepository` (from infrastructure). It may also manage DB sessions (e.g., binding a repo to a SQLAlchemy session from `core/database.get_db()`).
  * **Authentication/authorization**: e.g., `def get_current_user()` that checks the JWT token in the Authorization header (using `core/security.py` functions) and returns the current user or raises a 401 exception. Though this might be globally reused, if it’s module-specific, it can reside here.
  * Any other logic for preparing arguments for endpoints: e.g., verifying if an entity exists before reaching the endpoint (loading from repo and injecting, or raising 404 if not).

  In our example, a simple `get_example_repository`:

  ```python
  from app.modules.example.infrastructure.repositories import FooRepository
  from app.core.database import get_db

  def get_foo_repository(db=Depends(get_db)):
      return FooRepository(db_session=db)
  ```

  FastAPI will first resolve `get_db` (likely providing a per-request DB session), then pass that session to `FooRepository` and return the instance. The route function then receives a ready-to-use `FooRepository`, unaware of its creation details.

  Using `dependencies.py` promotes reuse and centralization: if we want to change how we obtain the repository (e.g., switch to a fake implementation for testing, or add caching), we do it in one place. It also simplifies route testing, as we can override dependencies in FastAPI’s TestClient if needed.

To summarize the structure of a **module**: the **Presentation** layer (routers) receives the request and uses **Dependencies** to get **Repositories** (Infra), then creates a **Use Case** (Application) to execute logic using **Entities/Services** (Domain), possibly persisting/querying via the repository, and returning the result which the router sends back to the client. Each part does its job and stays relatively isolated.

### `docs/` Directory (Documents)

The `docs/` folder is intended to store **external documentation** for the project. This is where you can place files like PDFs, specification documents, requirements, diagrams, design notes, or any other documentation artifacts that are useful to keep alongside the code repository, but that are not part of the application code itself.

For example:

* Client requirement documents in PDF/DOCX.
* Architecture or data model diagrams (editable formats or images).
* Research documentation or papers related to the project domain (e.g., AI papers, external API manuals).
* Any supplementary documentation to help onboard developers.

Keeping these files in `docs/` ensures the team has easy and version-controlled access to this material. Remember not to store sensitive information here unless encrypted, since it will be part of the repository (unless the repository is private and access is controlled).

### `scripts/` Directory (Useful Scripts)

The `scripts/` folder contains **helper scripts** used for project development or maintenance, but that **are not part of the running application code**. In other words, they are utilities run separately, usually for administrative tasks, support functions, or project setup.

In this template, for example:

* **`scripts/directory_tree.py`:** A Python script that likely generates the directory tree representation automatically (similar to the structure shown above). This type of script can be used to update the README documentation by listing new folders/files consistently.
* (Other scripts can be added as needed. Examples: a script to seed the database with test data, run lint/format across all modules, convert data files, etc.)

When creating scripts here, keep things organized and documented. It’s common to add a short header explaining the script’s purpose and how to use it.

**Important:** Scripts inside `scripts/` are not automatically executed by the main system (they are not imported in `app.py` or called by the app). They must be run manually (e.g., `uv run scripts/directory_tree.py` using uv, or activate the env and `python scripts/directory_tree.py`). Because of this, they may have extra dependencies or use code in isolation. Still, try to reuse project functions where it makes sense (e.g., a DB seed script could import an application repository to create records).

### `test/` Directory (Tests)

The `test/` folder contains the project’s **automated tests**. Here we adopt the convention of **mirroring the application's folder structure** inside `test/` to make it easier to locate tests corresponding to each part of the code.

Initial structure:

* **`test/core/`** – Folder for tests related to core (config, database, etc.). For example, testing if configuration variables are correctly loaded, or if logging is working.
* **`test/modules/`** – Folder for tests related to business modules. Inside it, we replicate each module.

  * `test/modules/example/` – Folder for tests of the example module. Inside it, we can create subfolders or files corresponding to the module’s layers:

    * We might have `test_domain.py`, `test_use_cases.py`, `test_repositories.py`, `test_routers.py`, etc., or even substructures like `domain/test_entities.py`, depending on preference.
    * In the template, only the `__init__.py` files are present to form the initial structure. It’s up to the developers to add test files as they implement features.

For example, if we implement a `CreateFooUseCase`, we’d create a unit test in `test/modules/example/test_use_cases.py` to verify expected behaviors (e.g., by passing a fake/in-memory repository to the use case). If we implement an endpoint in `routers.py`, we could write an integration test using FastAPI’s `TestClient` in `test/modules/example/test_routers.py` to call the API and check the responses.

**Best practices for tests:**

* Name test files according to what they test. Example: `test_entities.py` for entities, `test_services.py` for domain services, etc. Or organize by functionality: `test_crud_foo.py`, etc.
* Use testing frameworks like **pytest** (the de facto standard for FastAPI projects). Pytest is not explicitly listed in `pyproject.toml`, but can easily be added (e.g., via `uv add --group dev pytest`).
* Each test file or function should import the class/function to be tested from the appropriate layer. Keep dependencies isolated: when testing the Domain or Application layer, you can simulate infrastructure (use stubs/mocks for repositories).
* Infrastructure tests (e.g., real repository tests) may require a test database. Use pytest fixtures to set up and clean up (e.g., an in-memory SQLite DB, or transactions).
* Presentation/API tests can run with FastAPI’s **TestClient**, perhaps using `dependency_overrides` to inject “fake” repositories or a test connection.

The suggested structure makes it easy to quickly locate tests for a given feature. For example, if a developer modifies `app/modules/example/use_cases.py`, they’ll know that relevant tests are likely in `test/modules/example/test_use_cases.py`.

Remember to run tests regularly (e.g., via `uv run -- pytest`) to ensure everything keeps working as development progresses.

## Implementation Guide and Best Practices

This section consolidates guidelines for implementing new features following the architecture, and best practices the project should observe. The goal is to provide the team with a clear guide to the style and patterns to follow as the project evolves.

### Separation of Responsibilities and Layers

* **Don’t mix layers:** Each function/class should clearly belong to a single layer. Business rules go in domain or application, data access logic only in infrastructure, request/response handling only in presentation. Avoid, for instance, making DB calls directly in `routers.py` (Presentation) or using Pydantic models from `schemas.py` inside `domain` or `application`.
* **Pure domain:** Keep the code in `domain/` free of external dependencies. This includes not importing SQLAlchemy, FastAPI, requests/httpx, etc. If you need something external (e.g., a complex statistical calculation), it's okay to use calculation libraries—but not infrastructure-specific code.
* **Orchestrate in Application:** The Application layer (`use_cases`) is the coordinator. It calls whatever it needs from other layers. For example, to fulfill a request: the router calls the use case, which might call a domain service for complex rules, query a repository for data, apply logic, and ask the repository to save something. The application knows the domain (entities, services) and the repository interfaces. But it **does not know or decide** *how* the repository does its job. This lets us swap implementations without changing high-level logic.
* **Infrastructure can grow in detail without affecting business logic:** If we decide to switch databases (e.g., PostgreSQL to MongoDB) or AI providers, the changes should stay confined to `infrastructure/`, ideally without touching `domain/` or `application/`, except for small adjustments if the contract changes. This reinforces dependency inversion.
* **Keep presentation thin and simple:** Code in `routers.py` should be minimal, quickly delegating to use cases. It should handle HTTP aspects (status codes, auth via dependencies, route details), but not contain business logic. If you find yourself writing business rules inside a route function body, that code probably belongs in a use case or domain service.

In short, always ask yourself: “Which layer does this logic belong to?”
If it's response formatting or request parsing → Presentation;
If it's validation/business rule → Domain/Application;
If it's data access or external calls → Infrastructure.

### File and Code Naming Conventions

Maintaining consistent naming makes collaboration easier. Here are some conventions adopted in the template:

* **Folder and file names:** Use *lowercase letters*, with underscores (`_`) to separate words if necessary. Examples: `value_objects.py`, `my_module/`. Avoid spaces or special characters. The module name (folder inside `modules/`) should reflect the business context in singular form, preferably short and direct (e.g., `user`, `order`, `payment`). In the example, we use `example` as a generic name.
* **`__init__.py` files:** usually empty, only to declare the package. Sometimes used to facilitate imports (e.g., import and expose via `__all__`), but use this sparingly to avoid confusion.
* **Classes and Interfaces:** use **PascalCase** (CamelCase starting with an uppercase letter). Examples: `User`, `OrderRepository`, `ConsultarSaldoUseCase`. For abstract interfaces, you can prefix with I (e.g., `IUserRepository`), suffix with Interface, or use a simple descriptive name. The key is to make it clear from the context or docstring that it's abstract.
* **Functions and methods:** use **snake\_case** (lowercase\_with\_underscore). Names should be verbs or describe an action/result. Examples: `calcular_total()`, `execute()` (in use case), `obter_por_id()`.
* **Variables and attributes:** also in snake\_case. Avoid obscure abbreviations; be descriptive (e.g., `quantidade_itens` instead of `qtd` if possible).
* **Pydantic Schemas:** These are also classes, so PascalCase. Typically named with a suffix indicating their purpose: `XxxCreate`, `XxxUpdate`, `XxxOut`, etc.
* **Use Cases:** if implemented as classes, it's common to use the `UseCase` suffix for clarity (e.g., `FooUseCase`). Alternatively, some prefer naming use case classes with verbs and no suffix (e.g., `CriarFoo`), but here we adopt the suffix to avoid confusion with entities or services.
* **Test files:** name them starting with `test_`, and in parallel with the code they test. Example: `test_entities.py` for `entities.py`, or `test_routers.py` for `routers.py`. Within tests, use expressive function names (e.g., `def test_deve_calcular_total_corretamente():`).
* **Constants:** uppercase letters with underscores. Examples: `PI = 3.14`, or `MAX_TENTATIVAS = 5`.
* **Internal module names:** Subfolders follow the names `application, domain, infrastructure, presentation` as per the template convention. Keep these names if expanding the project to ensure consistency across modules.
* **Abstraction vs implementation prefixes:** If you create multiple implementations of an interface, such as different repositories (one SQL, one NoSQL), this can be reflected in the name: `UserRepositorySQL`, `UserRepositoryMongo`, both implementing `UserRepositoryInterface`. However, if there's only one implementation, a simple name like `UserRepository` is sufficient.

By following these conventions, the project code remains **readable**, and collaborators can quickly understand a file/class’s purpose from its name.

### Dependency Inversion and Dependency Injection

Dependency inversion is a fundamental principle in this architecture:

* **Abstractions in the core, implementations on the periphery:** Define interfaces for external functionality (persistence, email sending, etc.) in the Application or Domain layer, and implement them in the Infrastructure layer. This way, the core depends only on abstractions, not concrete details.
* **FastAPI Depends for injection:** Use FastAPI's dependency system to inject concrete implementations into routes. Instead of instantiating a repository inside the endpoint, use `Depends(get_repo)` so FastAPI handles it. This decouples the endpoint from the repo acquisition method (which might change or be replaced in tests).
* **Constructors receive dependencies:** In use case or service classes, inject dependencies via constructor (or setter/factory method). Avoid resolving global dependencies within logic (e.g., don’t directly call `FooRepository()` inside a use case; pass the repo as a parameter). This makes it easier to test in isolation (you pass a dummy repo).
* **Never the opposite:** The Infrastructure layer can import from Domain (e.g., an entity to build an object), but the Domain layer **must never** import anything from Infrastructure. If you see an import from infrastructure in `domain/` or `application/`, something is wrong. Check whether the dependency needs to be inverted via an interface.
* **Practical example:** In the example module, `application/interfaces.py` defines `FooRepositoryInterface`. `infrastructure/repositories.py` implements `FooRepository` which inherits from this interface. The use case in `application/use_cases.py` accepts a `FooRepositoryInterface`. In the route, we use `repo = Depends(get_foo_repository)` and pass it to the use case. Thus, the use case doesn’t know the exact repo class being used, just the interface. We could easily pass a test repository instead.
* **Root composition in app.py:** The main file `app.py` can be considered the final composition point of the application – where everything is assembled. For example, if we needed to create global instances or configure global injections, this would be the place. But generally, we keep things simple: each request assembles its own dependencies.

Respecting dependency inversion makes the system more resilient to changes and easier to reuse. For example, we could extract the domain + application layer into a separate library and swap the interface (e.g., from FastAPI to CLI), and the core logic would still work – this is a good mental test to see if dependencies are properly directed.

### Code Standards and Quality

* **Follows PEP8:** All Python code should adhere to PEP 8 (official style guide). This includes 4-space indentation, lines up to \~79 characters (ideally 100 max), snake\_case for functions/variables, etc. Use automated tools whenever possible.
* **Ruff (Linter):** This project includes [Ruff](https://github.com/astral-sh/ruff) as a development dependency (see `pyproject.toml`). Ruff is an extremely fast linter that helps detect style issues and possible bugs. Basic setup is configured. It's recommended to integrate Ruff into your editor or run it before commits (`uv run -- ruff .` or via pre-commit).
* **Type hints:** FastAPI heavily relies on type hints for validation and docs. Use **type annotations** throughout the code, not just in endpoints. This improves readability and helps tools like mypy (if static analysis is used). For example, declare return types and parameter types for functions and methods. E.g., `def salvar(self, foo: Foo) -> Foo:`.
* **Docstrings and comments:** Document public classes and functions with clear docstrings explaining the purpose, parameters, and return. For complex logic, use internal comments to explain specific parts. Remember, another developer (or your future self) will read and appreciate these clarifications.
* **Small functions, little repetition:** Follow the *DRY* (Don't Repeat Yourself) principle. If you notice duplicated code, consider refactoring into a utility function or service. Keep functions/methods short and cohesive – if a method is doing “too much,” it might need to be split.
* **Error handling:** Have a clear exception strategy. For example, create custom exceptions in the domain (e.g., `UsuarioNaoEncontradoError` in `domain/exceptions.py` if needed), and catch them in the presentation layer to return appropriate HTTP codes. Avoid unhandled exceptions reaching the presentation, as this results in generic 500 errors. It's better to catch and convert them into an HTTPException or return a friendly result.
* **Useful logs:** Use the configured logger (`logging.getLogger(__name__)`) at key points: logs for operation start/end, warnings for abnormal situations, errors for caught exceptions. Keep logs informative but not verbose. This helps in debugging and monitoring in production.
* **Configuration loading:** Use `core/config.py` and `.env` instead of spreading constants throughout the code. This way, changing a parameter (e.g., timeout for an external call) only requires changing the `.env` and possibly restarting the service, without touching code. It also facilitates different setups for dev/staging/prod.
* **Refactor frequently:** As features are added, keep the structure organized. If a module grows too large, consider subdividing it. For example, a `user` module might have sub-items like `user/domain/entities.py` etc., and if there are many entities, even a folder `entities/` with multiple files. The key is that the architecture serves the project; it can evolve. But any structural changes should be documented and communicated so everyone follows the same standard.

### Test Structuring

* **Unit vs integration testing:** Have unit tests for isolated functions (e.g., entity methods, internal domain service functions, use case logic without DB) and integration tests to ensure pieces work together (e.g., repository test accessing a real test DB, or full route test making a request).
* **Fixtures to set up scenarios:** Use **pytest** features like fixtures to create necessary objects. For example, a fixture that returns a fake repository populated with some data, to test a use case. Or a fixture that starts an in-memory database and creates tables to test repositories.
* **Tests in CI/CD:** If this template is used in real projects, test execution will be integrated into CI pipelines. Therefore, ensure tests don’t depend on local state (e.g., use test database defined via environment variable and clean between tests).
* **Test coverage:** Aim to cover critical functionalities. In particular, use cases (Application) and domain services deserve extensive testing as they carry business logic. Repositories can have tests to ensure queries are correct. Endpoints can have at least one happy-path test and some error tests.
* **Deterministic tests:** Tests should pass or fail consistently. If using randomness (e.g., in some AI component?), fix seeds or use mocks to control results, so the test is repeatable.
* **Running tests:** As mentioned, we can run via `pytest`. If using uv, a handy command: `uv run -- pytest -q` (`-q` is optional for quieter output). This ensures the right venv and dependencies are activated. Remember to configure `.env` if your config code needs it, or use `.env.test` during tests if we configure multi-environments.

By maintaining good test discipline, we gain confidence to evolve the project without fear of breaking existing functionality, since tests will alert us early to regressions.

## Project Dependencies

This template already includes some Python dependencies pre-installed and pre-configured as defined in `pyproject.toml` and `uv.lock`. Here's a summary of the main ones:

* **FastAPI (v0.115.13)** – Modern high-performance ASGI web framework, ideal for building RESTful APIs and easily integrating AI components. We use `fastapi[standard]`, which includes useful extras:

  * **Starlette (v0.46.2):** underlying ASGI framework for FastAPI, handles routing, middleware, WebSocket, etc.
  * **Uvicorn (v0.34.3):** high-performance ASGI server included via the "standard" extra, used to run the app.
  * **Email-validator, python-multipart, itsdangerous, PyYAML, httptools, websockets, etc.:** various libs included via `[standard]` to support forms, uploads, WebSockets, and other FastAPI features.
  * **FastAPI-CLI (v0.0.7):** command-line tool for managing FastAPI apps (included), e.g., run `python -m fastapi serve` to launch the API. (Optional; running uvicorn directly also works.)
  * **HTTPX (v0.28.1):** powerful async HTTP client, useful for calling external APIs (e.g., an AI service). Included as a dependency of fastapi\[standard].
  * **Jinja2 (v3.1.6):** templating engine included via Starlette (can be useful for generating HTML emails, for example).
* **Pydantic (v2.11.7):** Library for data validation and model creation, base for FastAPI schemas. Version 2 brings optimized performance via pydantic-core. We also use **pydantic-settings (v2.10.0)** for config handling (loading from .env).
* **UV (Astral)** – Package and environment manager. Creates the `.venv`, resolves dependencies (`uv.lock`), and executes commands in isolation. A modern alternative to pip/pipenv/poetry, offering speed and ease. (See next section for usage details.)
* **Ruff (v0.12.0)** – Linter for code quality. Included in the development dependencies group (`[tool.ruff]` in pyproject if configured). It checks PEP8, common errors, and even does some auto-fixes. Use it regularly to keep the code clean.
* *(Other possible dependencies not listed here can be added as needed, e.g., AI libraries like TensorFlow/PyTorch, ORMs like SQLAlchemy, or other utilities.)*

The **pre-installed dependency structure** can be visualized hierarchically as generated by `uv lock`, but the key point is that the main tools (FastAPI, Pydantic, etc.) are already available. To add new libraries, use `uv add library_name`, which will update both `pyproject` and `uv.lock`.

## Environment Setup and Running the App

Below are instructions to set up the development environment and run the template app. We cover from installing dependencies with uv to running via Docker.

### UV Package Manager

This project uses **uv** (by Astral) as the package and environment manager. UV is a modern tool combining the functions of pip, virtualenv, pip-tools, etc., making project management much easier. Key features of uv:

* Automatically creates an isolated virtual environment (`.venv`) for the project using the Python version specified in `.python-version`.
* Manages dependencies via `pyproject.toml` (general specs) and `uv.lock` (for locked versions), ensuring reproducibility.
* Simple commands to add/remove packages (`uv add`, `uv remove`), sync environments (`uv sync`), run scripts/commands in the venv (`uv run`), etc.
* Incredibly fast installation compared to traditional pip.

**Read the official uv documentation for more on [installation](https://docs.astral.sh/uv/getting-started/installation/).**

Once uv is available, ensure you're in the project directory (`fastapi-clean-architecture-ddd-template/`) when running uv commands, as it relies on the local `pyproject.toml`.

### Setting Up Environment Variables (.env)

Before running the app, configure your environment variables:

1. Copy the `.env.example` file and name it `.env` in the project root:

   ```bash
   cp .env.example .env
   ```

2. Open the `.env` file in an editor. By default, it may list example variables (likely empty or with placeholder values). Fill in each variable as appropriate:

   * Example: `APP_NAME="FastAPI Clean Architecture DDD Template"`, `DEBUG=true` or `false`, `DATABASE_URL="postgresql://user:password@localhost:5432/db"` etc.
   * If the app integrates with an external AI service, insert required API keys or endpoints here too (e.g., `OPENAI_API_KEY=...`), so the code in `core/config.py` can retrieve them.
   * **Do not use quotes** around values in `.env` (unless you want to include spaces). Pydantic Settings can interpret booleans (`true/false`) and numbers, but may treat everything as strings if not specified – conversion is usually handled by BaseSettings using type hints.

3. Check if `.env` is listed in `.gitignore` (it should be by default). Never commit this file with real credentials.

When running the app via uvicorn/uv, will uv automatically load `.env`? Actually, loading is done by our `Settings(BaseSettings)` code, which knows the env\_file. For safety, uv can also load .env if configured.

In summary, don’t skip this step. Without a properly configured `.env` (or exported variables), your app may use defaults or fail to start, depending on how `Settings` was implemented.

### Dependency Installation

With uv installed and `.env` configured, proceed to install the project dependencies in the virtual environment.

* **Sync the environment (install packages):**

  ```bash
  uv sync
  ```

  This command will make uv read the `pyproject.toml` and `uv.lock`. If the lockfile is present and compatible, it will install the exact versions listed in it into `.venv`. If you've added a new dependency to `pyproject.toml` and haven’t run lock yet, `uv sync` will also create/update the lockfile. Generally, after cloning the project, running `uv sync` ensures that your environment matches everyone else's.

  *Note:* The first execution will create the `.venv` directory and download the packages, which may take a few seconds. Subsequent runs will be faster if nothing has changed.

* **Activating the virtualenv (optional):** uv allows you to run commands without manually activating it (`uv run` handles that automatically). But if you want to enter the venv to run Python directly, do:

  * On Linux/macOS:

    ```bash
    source .venv/bin/activate
    ```
  * On Windows (PowerShell):

    ```powershell
    .venv\Scripts\Activate.ps1
    ```

  Once activated, you'll see the prefix `(.venv)` in the terminal. You can then use `python` or `pytest` directly. Don’t forget to `deactivate` when done. Again, this isn't strictly necessary if you always use `uv run`, but it's handy for familiarity.

* **Verifying the installation:** You can check if everything is okay by running:

  ```bash
  uv run python -V
  ```

  This should show the Python version (as per `.python-version`) and confirm that the command ran inside the venv. Or:

  ```bash
  uv run python -c "import fastapi; print(fastapi.__version__)"
  ```

  to print the installed FastAPI version, confirming it's accessible.

### Running the Application

With the environment set up, let’s run the FastAPI application locally. There are several ways:

* **Using uvicorn directly:**
  If the virtualenv is activated, simply run:

  ```bash
  uvicorn app.app:app --reload
  ```

  This starts the Uvicorn server pointing to the `app` object inside the `app.app` module (our FastAPI instance). The `--reload` flag enables automatic reloading when code changes (great for development).

  Without venv activated, you can run it via uv:

  ```bash
  uv run -- uvicorn app.app:app --reload
  ```

  The `uv run --` ensures uvicorn is executed within the isolated environment, even if you're outside the venv. Note that we're running uvicorn in development mode (default port 8000). Visit [http://localhost:8000/docs](http://localhost:8000/docs) to see the Swagger UI documentation generated automatically from the endpoints (currently, only those from the example module).

* **Using FastAPI-CLI:**
  Since we included fastapi-cli, another option is:

  ```bash
  uv run -- python -m fastapi app.app:app --reload
  ```

  This effectively does the same as uvicorn (the fastapi CLI uses uvicorn under the hood), so there's no significant difference. Use whichever approach you prefer.

Once the server is running, you should see Uvicorn logs in the console indicating the app is serving on port 8000. The interactive documentation (Swagger) will be available at `/docs` and the Redoc interface at `/redoc`. Initially, with the example module empty, the API may not have useful endpoints listed; as you add routes, they will appear there.

**Example module endpoints:** If you add some routes in `example/routers.py` (e.g., a status GET), they'll show up. The prefix can be configured in the router (e.g., `router = APIRouter(prefix="/foo", tags=["Foo"])` will place all routes under `/foo`). Make sure `app.py` includes the router (e.g., `app.include_router(example_router, prefix="/api/v1")` if you want a global prefix).

### Using Docker (Optional)

For those who prefer or need to run in a container (or prepare for production), this project provides Docker support:

* **Building the Docker image:** Make sure Docker is installed. In the project directory, run:

  ```bash
  docker build -t fastapi-clean-architecture-ddd-template:latest .
  ```

  This uses the provided **Dockerfile**. It likely performs steps such as:

  * Using a base image (e.g., `python:3.13-slim`).
  * Copying `pyproject.toml` and `uv.lock`, installing dependencies (this takes advantage of Docker cache if dependencies haven't changed).
  * Copying the rest of the code.
  * Setting the env variable `PYTHONPATH=/app` (if the code is copied to /app).
  * Running `uvicorn app.app:app` as the entrypoint (sometimes via `CMD`).

  Once done, you’ll have a local image named `fastapi-clean-architecture-ddd-template:latest`.

* **Running via standalone Docker:** Run a container from the image:

  ```bash
  docker run -d --env-file .env -p 8000:8000 fastapi-clean-architecture-ddd-template:latest
  ```

  This runs in the background (`-d`), loads variables from your local `.env` into the container, and maps port 8000 from the container to 8000 locally. Again, check [http://localhost:8000/docs](http://localhost:8000/docs) to verify it's up.

  *Note:* Use `docker logs <container_id>` to view logs, and `docker stop` to stop it when needed.

* **Docker Compose (multi-service development):** The `docker-compose.yaml` file makes it easier to spin up the app along with other services (if needed). For example, if the project needs a PostgreSQL database and maybe Redis, we could define in compose. You can edit it to add:

  ```yaml
  services:
    api:
      build: .
      env_file: .env
      ports:
        - "8000:8000"
    db:
      image: postgres:15
      environment:
        POSTGRES_USER: myuser
        POSTGRES_PASSWORD: mypass
        POSTGRES_DB: mydb
      ports:
        - "5432:5432"
  ```

  (This is an example; the actual template may differ.)

  Then run:

  ```bash
  docker-compose up --build
  ```

  This builds the image and starts both `api` and `db`. The app could read environment variables such as `DATABASE_URL=postgresql://myuser:mypass@db:5432/mydb`, pointing to the `db` container.

  Compose is very useful for development, as it allows you to mirror the production environment locally. Remember to shut it down with `docker-compose down` when not in use.

* **Hot-reload in Docker dev:** During development, you might want the container to reflect code changes without rebuilding the image every time. For this, you can map volumes in compose (mounting host code into the container) and run uvicorn in reload mode inside the container. Some extra adjustments are needed in the Dockerfile (like installing `uvicorn[standard]` in the container if not already, though it's included via `fastapi[standard]`) and in compose (mount `./app` to `/app/app`). This isn't configured out of the box, but can be set up if desired.

Using Docker in development is optional – you can absolutely use just uv + local venv. However, to standardize environments or if someone is on Windows and prefers a Linux container for alignment, it's available.

In production, using the resulting Docker image simplifies deployment (k8s, ECS, etc.), remembering to configure production environment variables and security/performance settings (e.g., run uvicorn without `--reload`, possibly with more workers, etc.).

## Final Considerations

This README aimed to cover **all aspects of the architecture** of the **fastapi-clean-architecture-ddd-template** project, including the purpose of each folder/file and best practices for implementation and maintenance. To recap some key points:

* The architecture follows **Clean Architecture** principles, separating domain, application, infrastructure, and presentation layers, making the code more modular, testable, and resilient to change.
* Each feature module inside `app/modules` is internally structured consistently, making it easy to add new modules following the example's model.
* Central config files (`core`) allow managing cross-cutting concerns (config, DB, logging, security) in a unified way.
* Dependency management via **uv** ensures reproducibility and ease of updating packages, while quality tools like **Ruff** keep the code standardized.
* The template already provides integration with Docker, .env for configuration, and test structure – take advantage of this by always writing tests when adding features, and ensuring they all pass before integrating changes.
* **Best coding practices** (PEP8, documentation, type hints, separation of concerns) are encouraged so that the project remains clean and understandable as it grows.
* For any questions, return to this document 😉. It should serve as a continuous reference. If something isn’t clear here, that’s a sign we should further improve the documentation.

With this template in hand, the team can start new projects faster and more uniformly, focusing on application-specific logic since the foundations (structure and basic config) are already prepared. Feel free to adjust details as needed for your specific project, but **maintain consistency** – this will make onboarding new devs easier and code sharing across sibling projects smoother.

Happy coding! 🚀 And remember: a well-defined architecture is a guide, but it should always serve the software’s purpose. Use it with flexibility and good judgment. Any contributions or improvements to the template itself can be discussed with the team so we can continuously evolve our standard base. Good coding!
