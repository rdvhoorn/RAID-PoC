import logging
import sys
import structlog
from logging import Logger
from utils.config import config

_configured = False

def configure_logging(dev_mode) -> None:
    # Set timestamp format
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    # Add processors to standard logging
    shared_processors = [
        timestamper, # timestamps in abovedefined format
        structlog.processors.add_log_level,         # i.e. info, error
        structlog.processors.StackInfoRenderer(),   # adds stack traces if log.exception is called
        structlog.processors.format_exc_info,       # formats exception tracebacks
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
    """ Gets a configured logger for your service """
    global _configured
    if not _configured:
        # Configure logger
        configure_logging(dev_mode)
        _configured = True
        
        # Emit "logger_initialized" after setup
        log = structlog.get_logger()
        init_log = log.bind(service=service) if service else log
        init_log.info("logger_initialized")

    # Get logger to return
    log = structlog.get_logger()
    return log.bind(service=service) if service else log
