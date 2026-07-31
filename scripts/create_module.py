import os
import sys

MODULE_STRUCTURE = {
    "": ["__init__.py"],
    "application": [
        "__init__.py",
        "exceptions.py",
        "interfaces.py",
        "mappers.py",
        "use_cases.py",
        "utils.py",
    ],
    "domain": ["__init__.py", "entities.py", "enums.py", "value_objects.py"],
    "infrastructure": [
        "__init__.py",
        "caches.py",
        "models.py",
        "repositories.py",
        "services.py",
    ],
    "presentation": [
        "__init__.py",
        "dependencies.py",
        "docs.py",
        "routers.py",
        "schemas.py",
    ],
}


def create_module(module_name: str) -> None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_path = os.path.join(project_root, "app", "modules", module_name)

    if os.path.exists(base_path):
        print(f"Error: module '{module_name}' already exists at {base_path}")
        sys.exit(1)

    for subdir, files in MODULE_STRUCTURE.items():
        dir_path = os.path.join(base_path, subdir) if subdir else base_path
        os.makedirs(dir_path, exist_ok=True)
        for filename in files:
            open(os.path.join(dir_path, filename), "w").close()

    test_path = os.path.join(project_root, "test", "modules", module_name)
    os.makedirs(test_path, exist_ok=True)
    open(os.path.join(test_path, "__init__.py"), "w").close()

    print(f"Module '{module_name}' created at {base_path}")
    print(f"Test folder created at {test_path}")


if __name__ == "__main__":
    name = input("Module name: ").strip().lower().replace(" ", "_").replace("-", "_")
    if not name:
        print("Error: module name cannot be empty")
        sys.exit(1)
    create_module(name)
