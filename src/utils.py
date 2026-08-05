"""
utils.py
========
Shared tools used across the whole project: logging setup and two
decorators (timer_decorator, log_errors) that other files borrow.
"""

import functools
import logging
import time

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

def get_logger(name: str) -> logging.Logger:
    """Create (or retrieve) a logger with the given name."""
    config.ensure_directories_exist()

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def timer_decorator(func):
    """Logs how long a function took to run."""
    logger = get_logger(func.__module__)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start_time
        logger.info(f"'{func.__name__}' finished in {elapsed:.3f} seconds")
        return result

    return wrapper


def log_errors(func):
    """Catches and logs any exception raised inside the wrapped function."""
    logger = get_logger(func.__module__)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            logger.error(f"Error in '{func.__name__}': {exc}", exc_info=True)
            raise

    return wrapper


if __name__ == "__main__":
    logger = get_logger(__name__)

    @timer_decorator
    @log_errors
    def sample_task(n: int) -> int:
        logger.info(f"Running sample_task with n={n}")
        return sum(i for i in range(n))

    result = sample_task(1_000_000)
    logger.info(f"Result: {result}")