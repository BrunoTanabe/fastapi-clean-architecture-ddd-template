import re
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.modules.shared.application.enums import ResponseMessages, Role
from app.modules.user.application.enums import Gender


# REQUEST
class CreateRequest(BaseModel):
    first_name: str = Field(
        title="First Name (Required)",
        description="The first name of the user.",
        min_length=3,
        max_length=100,
        examples=["John", "Jane"],
        json_schema_extra={
            "example": "John",
            "writeOnly": True,
        },
    )

    last_name: str = Field(
        title="Last Name (Required)",
        description="The last name of the user.",
        min_length=3,
        max_length=100,
        examples=["Doe", "Smith"],
        json_schema_extra={
            "example": "Doe",
        },
    )

    preferred_name: Optional[str] = Field(
        title="Preferred Name (Optional)",
        description="The preferred name of the user.",
        max_length=100,
        examples=["Joe", "Jan"],
        json_schema_extra={
            "example": "Joe",
            "writeOnly": True,
        },
    )

    gender: Gender = Field(
        title="Gender (Required)",
        description=f"The gender of the user. Must be one of the following: {', '.join([gender.value for gender in Gender])}.",
        examples=[Gender.MALE.value, Gender.FEMALE.value],
        json_schema_extra={
            "example": Gender.MALE.value,
            "writeOnly": True,
        },
    )

    birthdate: date = Field(
        title="Birthdate (Required)",
        description="The birthdate of the user. The user must be at least 18 years old.",
        examples=["1995-01-01", "2000-12-31"],
        json_schema_extra={
            "example": "1995-01-01",
            "writeOnly": True,
        },
    )

    email: str = Field(
        title="User Email (Required)",
        description="The email address of the user.",
        min_length=3,
        max_length=100,
        examples=["johndoe@domain.com", "jane.smith@email.com"],
        json_schema_extra={
            "example": "johndoe@domain.com",
            "writeOnly": True,
        },
    )

    phone: Optional[str] = Field(
        default=None,
        title="Phone (Optional)",
        description="The phone number of the user in international format (e.g., +555472664275).",
        examples=["+555472664275", "+18005550199"],
        json_schema_extra={
            "example": "+555472664275",
            "writeOnly": True,
        },
    )

    password: str = Field(
        title="Password (Required)",
        description="The password of the user. The password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.",
        min_length=8,
        max_length=64,
        examples=["MyP@ssword123", "S3cur3P@ss!"],
        json_schema_extra={
            "example": "MyP@ssword123",
            "writeOnly": True,
        },
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, request: str) -> str:
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$", request):
            raise ValueError(
                "Name must contain only letters, spaces, apostrophes, and hyphens."
            )
        return request

    @field_validator("preferred_name")
    @classmethod
    def validate_preferred_name(cls, request: Optional[str]) -> Optional[str]:
        if isinstance(request, str) and request.strip() == "":
            return None
        return request

    @field_validator("birthdate")
    @classmethod
    def validate_birthdate(cls, request: date) -> date:
        today = date.today()
        min_year = date(1900, 1, 1)
        if request > today:
            raise ValueError("Birthdate cannot be a future date.")
        if request < min_year:
            raise ValueError("Birthdate cannot be before January 1, 1900.")
        return request

    @field_validator("email")
    @classmethod
    def validate_email(cls, request: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", request):
            raise ValueError("Invalid email address.")
        return request.lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, request: Optional[str]) -> Optional[str]:
        if request is None:
            return request
        if isinstance(request, str) and request.strip() == "":
            return None
        stripped = re.sub(r"[\+\-\(\)]", "", request)
        if not stripped.isdigit():
            raise ValueError(
                "Phone number must contain only digits, '+', '-', '(' and ')'."
            )
        if not (7 <= len(stripped) <= 15):
            raise ValueError("Phone number must have between 7 and 15 digits.")
        return request

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if len(password) > 64:
            raise ValueError("Password must be at most 64 characters long.")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", password):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain at least one special character.")

        return password

    model_config = ConfigDict(
        title="CreateRequest",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Request model for creating a new user.",
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "preferred_name": "Joe",
                "gender": Gender.MALE.value,
                "birthdate": "1995-01-01",
                "email": "johndoe@domain.com",
                "phone": "+555472664275",
                "password": "MyP@ssword123",
            },
            "examples": [
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "preferred_name": "Joe",
                    "gender": Gender.MALE.value,
                    "birthdate": "1995-01-01",
                    "email": "johndoe@domain.com",
                    "phone": "+555472664275",
                    "password": "MyP@ssword123",
                },
                {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "preferred_name": "Jan",
                    "gender": Gender.FEMALE.value,
                    "birthdate": "2000-12-31",
                    "email": "jane.smith@email.com",
                    "phone": "+18005550199",
                    "password": "S3cur3P@ss!",
                },
            ],
        },
    )


# RESPONSE
class CreateResponse(BaseModel):
    message: str = ResponseMessages.CREATED.value

    model_config = ConfigDict(
        title="CreateResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for creating a new user.",
            "example": {"message": ResponseMessages.CREATED.value},
        },
    )


class MeResponse(BaseModel):
    first_name: str = Field(
        title="First Name (Required)",
        description="The first name of the user.",
        examples=["John", "Jane"],
        json_schema_extra={
            "example": "John",
            "readOnly": True,
        },
    )

    last_name: str = Field(
        title="Last Name (Required)",
        description="The last name of the user.",
        examples=["Doe", "Smith"],
        json_schema_extra={
            "example": "Doe",
            "readOnly": True,
        },
    )

    preferred_name: str = Field(
        title="Preferred Name (Required)",
        description="The preferred name of the user to be used in the system, to be displayed to other users, and to LLM model references.",
        examples=["Joe", "Jan"],
        json_schema_extra={
            "example": "Joe",
            "readOnly": True,
        },
    )

    gender: Gender = Field(
        title="Gender (Required)",
        description=f"The gender of the user. Must be one of the following: {', '.join([gender.value for gender in Gender])}.",
        examples=[Gender.MALE.value, Gender.FEMALE.value],
        json_schema_extra={
            "example": Gender.MALE.value,
            "readOnly": True,
        },
    )

    birthdate: date = Field(
        title="Birthdate (Required)",
        description="The birthdate of the user.",
        examples=["1990-01-01", "2000-12-31"],
        json_schema_extra={
            "example": "1990-01-01",
        },
    )

    email: str = Field(
        title="User Email (Required)",
        description="The email address of the user registered in the system.",
        examples=["johndoe@domain.com", "jane.smith@email.com"],
        json_schema_extra={
            "example": "johndoe@domain.com",
            "readOnly": True,
        },
    )

    phone: Optional[str] = Field(
        default=None,
        title="Phone (Optional)",
        description="The phone number of the user in international format (e.g., +555472664275).",
        examples=["+555472664275", "+18005550199"],
        json_schema_extra={
            "example": "+555472664275",
            "readOnly": True,
        },
    )

    role: Role = Field(
        title="User Role (Required)",
        description="The role of the user in the system.",
        examples=[Role.ADMIN.value, Role.MANAGER.value],
        json_schema_extra={
            "example": Role.ADMIN.value,
            "readOnly": True,
        },
    )

    created_at: datetime = Field(
        title="Created At (Required)",
        description="The date and time when the user was created in the system.",
        examples=["2024-05-01T12:00:00Z", "2024-05-01T15:30:00+00:00"],
        json_schema_extra={
            "example": "2024-05-01T12:00:00Z",
            "readOnly": True,
        },
    )

    model_config = ConfigDict(
        title="MeResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for retrieving information about the current user.",
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "preferred_name": "Joe",
                "gender": Gender.MALE.value,
                "birthdate": "1995-01-01",
                "email": "johndoe@domain.com",
                "phone": "+555472664275",
                "role": Role.ADMIN.value,
                "created_at": "2024-05-01T12:00:00Z",
            },
            "examples": [
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "preferred_name": "Joe",
                    "gender": Gender.MALE.value,
                    "birthdate": "1995-01-01",
                    "email": "johndoe@domain.com",
                    "phone": "+555472664275",
                    "role": Role.ADMIN.value,
                    "created_at": "2024-05-01T12:00:00Z",
                },
                {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "preferred_name": "Jan",
                    "gender": Gender.FEMALE.value,
                    "birthdate": "2000-12-31",
                    "email": "jane.smith@email.com",
                    "phone": "+18005550199",
                    "role": Role.USER.value,
                    "created_at": "2024-05-01T15:30:00+00:00",
                },
            ],
        },
    )
