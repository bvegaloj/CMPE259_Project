"""
Logger Configuration for SJSU Virtual Assistant
Provides logging functionality for the application
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logger(
    name: str = "sjsu_assistant",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "./logs"
) -> logging.Logger:
    """
    Set up and configure logger
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file name (will be created in log_dir)
        log_dir: Directory for log files
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file specified)
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Create file handler
        file_path = log_path / log_file
        file_handler = logging.FileHandler(file_path, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {file_path}")
    
    return logger


def get_logger(name: str = "sjsu_assistant") -> logging.Logger:
    """
    Get existing logger or create default one
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set up default configuration
    if not logger.handlers:
        setup_logger(name)
    
    return logger


def create_session_log(log_dir: str = "./logs") -> str:
    """
    Create a log file for the current session
    
    Args:
        log_dir: Directory for log files
        
    Returns:
        Path to the created log file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"session_{timestamp}.log"
    
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    return str(log_path / log_file)


def log_agent_step(
    logger: logging.Logger,
    step_number: int,
    thought: str,
    action: str,
    observation: str
):
    """
    Log an agent reasoning step
    
    Args:
        logger: Logger instance
        step_number: Step number
        thought: Agent's thought
        action: Action taken
        observation: Observation result
    """
    logger.info(f"Step {step_number}:")
    logger.info(f"  Thought: {thought[:100]}..." if len(thought) > 100 else f"  Thought: {thought}")
    logger.info(f"  Action: {action}")
    logger.info(f"  Observation: {observation[:100]}..." if len(observation) > 100 else f"  Observation: {observation}")


def log_query(logger: logging.Logger, query: str, response: str, response_time: float):
    """
    Log a query and response
    
    Args:
        logger: Logger instance
        query: User query
        response: Agent response
        response_time: Time taken to respond
    """
    logger.info(f"Query: {query}")
    logger.info(f"Response time: {response_time:.2f}s")
    logger.debug(f"Response: {response}")


def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """
    Log an error with context
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context about the error
    """
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg = f"{context} - {error_msg}"
    
    logger.error(error_msg, exc_info=True)


def log_evaluation_result(
    logger: logging.Logger,
    query_id: str,
    completeness: float,
    relevance: float,
    response_time: float
):
    """
    Log evaluation metrics
    
    Args:
        logger: Logger instance
        query_id: Query identifier
        completeness: Completeness score
        relevance: Relevance score
        response_time: Response time
    """
    logger.info(f"Evaluation - Query ID: {query_id}")
    logger.info(f"  Completeness: {completeness:.2f}")
    logger.info(f"  Relevance: {relevance:.2f}")
    logger.info(f"  Response Time: {response_time:.2f}s")


class LoggerContext:
    """Context manager for temporary logger configuration"""
    
    def __init__(self, logger: logging.Logger, level: str):
        """
        Initialize logger context
        
        Args:
            logger: Logger instance
            level: Temporary log level
        """
        self.logger = logger
        self.new_level = getattr(logging, level.upper())
        self.old_level = logger.level
    
    def __enter__(self):
        """Set new log level"""
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore old log level"""
        self.logger.setLevel(self.old_level)


def set_log_level(logger: logging.Logger, level: str):
    """
    Set logger level
    
    Args:
        logger: Logger instance
        level: New log level
    """
    logger.setLevel(getattr(logging, level.upper()))
    logger.info(f"Log level set to {level.upper()}")
