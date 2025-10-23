from enum import Enum


class ResponseMessages(Enum):
    # SUCCESS MESSAGES
    SUCCESS = "Request processed successfully"
    CREATED = "Resource created successfully"
    UPDATED = "Resource updated successfully"
    DELETED = "Resource deleted successfully"
    RETRIEVED = "Resource retrieved successfully"
    REDIRECT = "Redirecting to the requested resource"
    REDIRECT_AUTHENTICATION_NOTICE = "Continue authentication in the link provided"

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

    # SERVER ERROR MESSAGES
    BAD_GATEWAY = "Bad gateway"
    INTERNAL_ERROR = "Internal processing error"
    DATABASE_ERROR = "Database operation error"
    SERVICE_UNAVAILABLE = "Service temporarily unavailable"
    GATEWAY_TIMEOUT = "Gateway timeout"

    # AUTHENTICATION & AUTHORIZATION SPECIFIC
    TOKEN_EXPIRED = "Authentication token expired"
    TOKEN_INVALID = "Invalid authentication token"
    INSUFFICIENT_PERMISSIONS = "Insufficient permissions"
    ACCOUNT_DISABLED = "Account is disabled"
    SESSION_EXPIRED = "Session has expired"

    # DATABASE OPERATIONS
    DATABASE_CONNECTION_ERROR = "Database connection failed"
    TRANSACTION_FAILED = "Database transaction failed"
    DUPLICATE_ENTRY = "Duplicate entry detected"
    CONSTRAINT_VIOLATION = "Database constraint violation"

    # FILE OPERATIONS
    FILE_NOT_FOUND = "File not found"
    FILE_UPLOAD_FAILED = "File upload failed"
    FILE_TOO_LARGE = "File size exceeds limit"
    INVALID_FILE_FORMAT = "Invalid file format"

    # EXTERNAL SERVICES
    EXTERNAL_SERVICE_ERROR = "External service error"
    API_QUOTA_EXCEEDED = "API quota exceeded"
    THIRD_PARTY_TIMEOUT = "Third-party service timeout"

    # CUSTOM APPLICATION MESSAGES
    STARTUP_SUCCESS = "Application started successfully"
    SHUTDOWN_SUCCESS = "Application shutdown completed"
    MAINTENANCE_MODE = "Service under maintenance"
    FEATURE_DISABLED = "Feature is currently disabled"

    # OAUTH SPECIFIC
    OAUTH_CALLBACK_SUCCESS = "OAuth authentication completed"
    OAUTH_CALLBACK_ERROR = "OAuth authentication failed"
    OAUTH_TOKEN_REFRESH_FAILED = "Failed to refresh OAuth token"

    # CHAT/AI SPECIFIC
    CHAT_CREATED = "Chat session created successfully"
    MESSAGE_SENT = "Message sent successfully"
    AI_RESPONSE_ERROR = "Failed to generate AI response"
    CONVERSATION_LIMIT_REACHED = "Conversation limit reached"
