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
  * [Using Makefile](#using-makefile)
* [Database Migrations](#database-migrations)
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
* **Makefile:** A file containing a set of directives used by the `make` build automation tool. It provides convenient shortcuts for common tasks such as starting the application with Docker, running tests, or cleaning up the environment. For example, `make start` can be used to spin up the Docker containers.
* **alembic.ini:** Configuration file for **Alembic**, a lightweight database migration tool for usage with the SQLAlchemy Database Toolkit for Python. It defines how migrations should be run, where the migration scripts are located, and how to connect to the database for migration purposes.
* **migrations/**: Directory containing database migration scripts. This folder is managed by Alembic and stores the version history of the database schema. Each modification to the database structure is stored as a separate revision script here.
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
  * Loads initial settings (e.g., setting log level from `core/logging.py`, or reading configs from `core/security.py`).
  * Includes each module’s routers using `app.include_router(...)`, registering the routes from the different parts of the API.
  * Defines startup or shutdown event handlers if needed (e.g., a `lifespan` function to connect to the database via `core/database.py`).

  In short, `app.py` assembles the application by composing pieces defined elsewhere. This file (more precisely, the `app` object in it) is what you point to when running the server.

* **`__init__.py`:** An empty (or nearly empty) file whose only purpose is to mark `app` as a Python package. There’s no need to put logic here, though you could use it to set up global imports if desired (keeping it empty for simplicity is fine).

#### `app/core/` Directory (Central Configuration)

The `app/core` package contains foundational configuration modules and utilities for the application. These are low-level or cross-cutting components that are usually used by multiple parts of the system. Details of the files inside `core/`:

* **`core/database.py`:** Module responsible for setting up the database connection or other persistent data resources. It uses SQLAlchemy with asynchronous support (`asyncpg`). It configures the connection engine using the DB URL from the settings (`settings.database_url`), creates an asynchronous session maker (`async_sessionmaker`), and provides utility functions to obtain a session (to be used as a FastAPI dependency). This module also handles database initialization and connection management.
* **`core/exception_handler.py`:** Centralized exception handling logic. It defines how the application responds to various errors, ensuring consistent error responses (e.g., JSON format with error codes) across the API.
* **`core/logging.py`:** logging configuration using `loguru`. configured to intercept standard python logging messages and format them for better readability and structure, supporting different log levels and outputs (console, file, etc.).
* **`core/middleware.py`:** contains middleware definitions for processing requests and responses globally. examples include cors configuration, request timing, or request id injection.
* **`core/migrations.py`:** utilities for programmatically running database migrations, possibly integrated into the application startup or a separate management command.
* **`core/resources.py`:** manages shared resources or constants used throughout the application.
* **`core/security.py`:** handles security-related implementing mechanisms like password hashing (using argon2), jwt (json web token) generation and validation, and cookie management for secure session handling. it provides utilities for encrypting/decrypting sensitive data and verifying user credentials.
* **`core/settings.py`:** defines the application's configuration schema using `pydantic-settings`. it reads environment variables from `.env` files and maps them to typed python objects, validating configuration values at startup.

#### `app/modules/` Directory (Feature Modules)

This directory contains the feature-specific modules of the application. Each module (e.g., `authentication`, `user`, `example`) follows a DDD-inspired structure with layers:

* **Authentication (`app/modules/authentication/`):**
  * Manages user login, logout, and token refreshing.
  * Handles JWT creation and cookie setting for secure authentication.
  * **Presentation:** Routers for `/auth/login`, `/auth/logout`, `/auth/refresh`.
  * **Domain:** Entities like `Token`, `UserCredentials`.
  * **Application:** Use cases for verifying credentials and generating tokens.

* **User (`app/modules/user/`):**
  * Manages user accounts (registration, profile updates, retrieval).
  * **Presentation:** Routers for `/users/` (CRUD operations).
  * **Domain:** User entity and rules.
  * **Application:** Use cases for creating and managing users.

* **Example Module (`app/modules/example/`):**
  * A template module demonstrating the architectural pattern.

Each module typically has verify structure:
* **Domain:** `entities.py`, `value_objects.py`, `services.py` (Pure business logic).
* **Application:** `use_cases.py`, `interfaces.py`, `dtos.py` (Orchestration).
* **Infrastructure:** `repositories.py`, `models.py` (Database implementation).
* **Presentation:** `routers.py`, `schemas.py` (API endpoints).

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

The project relies on a modern stack of Python libraries to ensure performance, security, and maintainability. Key dependencies include:

*   **FastAPI** (`fastapi[standard]>=0.135.1`): High-performance web framework for building APIs with Python.
*   **Alembic** (`alembic>=1.18.4`): Database migration tool for SQLAlchemy.
*   **SQLAlchemy** (`sqlalchemy>=2.0.48`): SQL toolkit and Object-Relational Mapping (ORM) library.
*   **AsyncPG** (`asyncpg>=0.31.0`): A fast PostgreSQL database client library for Python asyncio.
*   **Psycopg** (`psycopg>=3.3.3`, `psycopg-binary`): PostgreSQL adapter for Python.
*   **Pydantic** (`pydantic>=2.12.5`): Data validation and settings management using Python type hints.
*   **Pydantic Settings** (`pydantic-settings>=2.13.1`): Management of environment using Pydantic.
*   **Cryptography** (`cryptography>=46.0.5`): Library for cryptographic recipes and primitives.
*   **JWCrypto** (`jwcrypto>=1.5.6`): Implementation of JSON Web Token (JWT) standards.
*   **PWDLib** (`pwdlib[argon2]>=0.3.0`): Modern password hashing (Argon2).
*   **Loguru** (`loguru>=0.7.3`): Python logging made (stupidly) simple.
*   **Orjson** (`orjson>=3.11.7`): Fast, correct Python JSON library.
*   **Hypercorn** (`hypercorn>=0.18.0`): ASGI server to run the application.
*   **Py-Automapper** (`py-automapper>=2.2.0`): Object mapping library.
*   **Stackprinter** (`stackprinter>=0.2.12`): Friendly stack trace formatting.

Dev dependencies:
*   **Ruff**: An extremely fast Python linter and code formatter.

## Environment Setup and Execution

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

If you prefer to run with Docker (recommended for consistency), ensure you have `docker` and `docker-compose` installed.

1.  **Build and Run**:
    ```sh
    docker-compose up --build
    ```
    This will start the API and any dependencies (DB, etc.).

2.  **Access**:
    The API should be available at `http://localhost:8000` (or the configured port).

### Using Makefile

The project includes a `Makefile` to simplify common development tasks. Run these commands from the project root:

*   `make start`: Starts the application and dependencies (DB, etc.) using Docker Compose (rebuilds if necessary).
*   `make start-silent`: Same as `start` but runs containers in the background (detached mode).
*   `make view-processes`: Lists running Docker containers.
*   `make delete`: Stops modules and removes containers, networks, and volumes.
*   `make dependencies-up`: Starts only the database services (Postgres, Admin).
*   `make dependencies-up-silent`: Starts database services in the background.
*   `make dependencies-down`: Stops and removes database services.

### Database Migrations

Database schema changes are managed using **Alembic**.

1.  **Create a new migration:**
    When you modify your SQLAlchemy models (e.g., in `infrastructure/models.py`), generate a migration script:
    ```bash
    alembic revision --autogenerate -m "Description of change"
    ```
    This creates a new file in `migrations/versions/`.

2.  **Apply migrations:**
    To upgrade the database to the latest version:
    ```bash
    alembic upgrade head
    ```

3.  **Downgrade:**
    To revert the last migration:
    ```bash
    alembic downgrade -1
    ```

### Authentication & Cookie Management

The application implements secure authentication using **JWT (JSON Web Tokens)** and **HttpOnly Cookies**.

*   **Login Flow:**
    *   Endpoint: `POST /api/v1/auth/login`
    *   Returns access and refresh tokens set as **HttpOnly cookies**.
    *   This prevents JavaScript access to tokens, mitigating XSS attacks.

*   **Security Features:**
    *   **Password Hashing:** Uses **Argon2** via `pwdlib` for robust password security.
    *   **Token Rotation:** Refresh tokens allow obtaining new access tokens without re-login.
    *   **Encryption:** Sensitive data is encrypted using `cryptography` library.

### Best Practices & Code Examples

Here are examples of how to implement standard components efficiently following the architecture.

#### 1. Repository Implementation (Infrastructure)
Use `SQLAlchemy` with `async` sessions.

```python
# app/modules/authentication/infrastructure/repositories.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.authentication.domain.entities import User
from app.modules.authentication.infrastructure.models import UserModel

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalars().first()
        return model.to_entity() if model else None

    async def save(self, user: User) -> User:
        model = UserModel.from_entity(user)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_entity()
```

#### 2. Use Case (Application)
Orchestrates domain logic and repositories.

```python
# app/modules/authentication/application/use_cases.py

class AuthenticateUserUseCase:
    def __init__(self, user_repository: UserRepository, password_service: PasswordService):
        self.user_repository = user_repository
        self.password_service = password_service

    async def execute(self, command: LoginCommand) -> AuthTokens:
        user = await self.user_repository.get_by_email(command.email)
        if not user or not self.password_service.verify(command.password, user.password_hash):
            raise InvalidCredentialsException()
        
        return self.token_service.generate_tokens(user)
```

#### 3. Router (Presentation)
Handles HTTP requests and dependency injection.

```python
# app/modules/authentication/presentation/routers.py

@router.post("/login", response_model=TokenSchema)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_use_case)
):
    tokens = await use_case.execute(LoginCommand(email=form_data.username, password=form_data.password))
    response = JSONResponse(content={"message": "Login successful"})
    set_auth_cookies(response, tokens)
    return response
```

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
