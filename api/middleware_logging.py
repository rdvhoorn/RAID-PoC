from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4
from fastapi import Request
import structlog

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware to manage and inject a unique request ID for every incoming HTTP request.

    Features:
    - Extracts the request ID from the "X-Request-ID" header if present.
    - If not present, generates a new UUID4-based request ID.
    - Binds a structlog logger with the request ID and attaches it to `request.state.logger`,
      so it can be used in route handlers for consistent contextual logging.
    - Logs "request_started" at the beginning of the request with method and path.
    - Logs "request_completed" after processing the request with the status code.
    - Catches and logs any unhandled exceptions with full traceback.
    - Adds the request ID to the response headers under "X-Request-ID" for traceability.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Use incoming X-Request-ID or generate one
        request_id = request.headers.get("X-Request-ID", str(uuid4()))

        # Bind a request-specific logger
        log = structlog.get_logger().bind(request_id=request_id)

        # Attach logger to request.state
        request.state.logger = log

        # Log the request
        log.info("request_started", method=request.method, path=request.url.path)

        try:
            response = await call_next(request)
        except Exception as e:
            log.exception("unhandled_exception")
            raise

        # Add request_id to response headers
        response.headers["X-Request-ID"] = request_id

        log.info("request_completed", status_code=response.status_code)
        return response
