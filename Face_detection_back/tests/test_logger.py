"""Unit tests for logger module."""
import pytest
import logging
from app.logger import get_logger, setup_logging


class TestLogger:
    """Test cases for logger configuration."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger(__name__)
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == __name__

    def test_logger_has_handlers_after_setup(self):
        """Test that logger has handlers configured after setup."""
        setup_logging()
        logger = get_logger("test_module")
        
        # Root logger should have handlers
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0

    def test_logger_level_after_setup(self):
        """Test logger level configuration after setup."""
        setup_logging()
        root_logger = logging.getLogger()
        
        assert root_logger.level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]

    def test_multiple_loggers_different_names(self):
        """Test creating multiple loggers with different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger1 is not logger2

    def test_logger_can_log_messages(self):
        """Test that logger can log messages without errors."""
        setup_logging()
        logger = get_logger("test_logging")
        
        try:
            logger.info("Test info message")
            logger.debug("Test debug message")
            logger.warning("Test warning message")
            logger.error("Test error message")
        except Exception as e:
            pytest.fail(f"Logger raised exception: {e}")

