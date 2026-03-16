from enum import Enum


class ApplicationEnvironment(str, Enum):
    DEV = "dev"
    HOMOLOG = "homolog"
    PRODUCTION = "production"


class ResponseMessages(Enum):
    # SUCCESS MESSAGES
    SUCCESS = "Request processed successfully"
    CREATED = "Resource created successfully"
    UPDATED = "Resource updated successfully"
    DELETED = "Resource deleted successfully"
    RETRIEVED = "Resource retrieved successfully"
    REDIRECT = "Redirecting to the requested resource"
    REDIRECT_AUTHENTICATION_NOTICE = "Continue authentication in the link provided"
    LOGIN_SUCCESS = "User logged in successfully"
    REFRESH_SUCCESS = "Refresh token generated successfully"
    LOGOUT_SUCCESS = "User logged out successfully"

    # CLIENT ERROR MESSAGES
    BAD_REQUEST = "Invalid request parameters"
    UNAUTHORIZED_ERROR = "Unauthorized access"
    AUTHENTICATION_ERROR = "Authentication error"
    AUTHORIZATION_ERROR = "Authorization error"
    RESOURCE_NOT_FOUND = "Resource not found"
    METHOD_ERROR = "Method error"
    VALIDATION_ERROR = "Form validation error"
    CONFLICT = "Resource already exists"
    UNSUPPORTED_MEDIA_TYPE = "Unsupported media type"
    RATE_LIMIT_EXCEEDED = "Rate limit exceeded"
    PAYLOAD_TOO_LARGE = "Request payload too large"
    METHOD_NOT_ALLOWED = "Method not allowed"
    FORBIDDEN = "Forbidden action or resource"

    # SERVER ERROR MESSAGES
    BAD_GATEWAY = "Bad gateway"
    INTERNAL_ERROR = "Internal processing error"
    DATABASE_ERROR = "Database operation error"
    SERVICE_UNAVAILABLE = "Service temporarily unavailable"
    GATEWAY_TIMEOUT = "Gateway timeout"


class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
