import logging
import sys
import structlog
import os
from logging import Logger
from utils.config import config

_configured = False

def configure_logging(dev_mode) -> None:
    # Add processors to standard logging
    shared_processors = [
        # Adds a "level" field to each log (e.g. "info", "error") so it's queryable in log systems
        structlog.processors.add_log_level,

        # If you use log.exception(), this adds the full stack trace into the log entry
        structlog.processors.StackInfoRenderer(),

        # Formats exception tracebacks (from exc_info=True or log.exception) nicely
        structlog.processors.format_exc_info,

        # Adds an ISO-8601 timestamp under the "timestamp" key (default output format for most log systems)
        structlog.processors.TimeStamper(fmt="iso"),
        
        structlog.contextvars.merge_contextvars
    ]

    # If in devmode, add console colors, otherwise, just log jsons without colors (for prod env)
    if dev_mode:
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    else:
        renderer = structlog.processors.JSONRenderer()

    # Core config initialization
    structlog.configure(
        processors=shared_processors + [renderer],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )


def get_and_configure_logger(service: str = None, dev_mode=config["DEVELOPER_MODE"]) -> Logger:
    if service is None:
        env_service = os.getenv("SERVICE_NAME", None)
        if env_service:
            service = env_service
    
    global _configured
    if not _configured:
        configure_logging(dev_mode)
        _configured = True

        # Bind global context
        if service:
            structlog.contextvars.bind_contextvars(service=service)

        structlog.get_logger().info("logger_initialized")

    return structlog.get_logger()

