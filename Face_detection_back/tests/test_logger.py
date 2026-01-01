"""Unit tests for logger module."""
import pytest
import logging
from app.logger import get_logger


class TestLogger:
    """Test cases for logger configuration."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger(__name__)
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == __name__

    def test_logger_has_handlers(self):
        """Test that logger has handlers configured."""
        logger = get_logger("test_module")
        
        assert len(logger.handlers) > 0

    def test_logger_level(self):
        """Test logger level configuration."""
        logger = get_logger("test_level")
        
        assert logger.level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]

    def test_multiple_loggers_different_names(self):
        """Test creating multiple loggers with different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger1 is not logger2

    def test_logger_can_log_messages(self):
        """Test that logger can log messages without errors."""
        logger = get_logger("test_logging")
        
        try:
            logger.info("Test info message")
            logger.debug("Test debug message")
            logger.warning("Test warning message")
            logger.error("Test error message")
        except Exception as e:
            pytest.fail(f"Logger raised exception: {e}")
