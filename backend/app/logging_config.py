"""
Production Logging Configuration for QuantumCertify
"""
import os
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any
import json


class ProductionFormatter(logging.Formatter):
    """
    Custom formatter for production logging with JSON output and sensitive data filtering
    """
    
    SENSITIVE_FIELDS = {
        'password', 'secret', 'key', 'token', 'api_key', 
        'db_password', 'gemini_api_key', 'jwt_secret'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Create log entry dictionary
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': os.getpid(),
            'thread_id': record.thread,
            'environment': os.getenv('ENVIRONMENT', 'development')
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            filtered_extra = self._filter_sensitive_data(record.extra_data)
            log_entry.update(filtered_extra)
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': self.formatException(record.exc_info)
            }
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address
        
        return json.dumps(log_entry, ensure_ascii=False)
    
    def _filter_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter sensitive data from log entries"""
        if not isinstance(data, dict):
            return data
        
        filtered = {}
        for key, value in data.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in self.SENSITIVE_FIELDS):
                filtered[key] = "[REDACTED]"
            elif isinstance(value, dict):
                filtered[key] = self._filter_sensitive_data(value)
            else:
                filtered[key] = value
        
        return filtered


def setup_production_logging():
    """
    Configure production logging with appropriate handlers and formatters
    """
    # Get configuration from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_format = os.getenv('LOG_FORMAT', 'json').lower()
    enable_access_logs = os.getenv('ENABLE_ACCESS_LOGS', 'true').lower() == 'true'
    environment = os.getenv('ENVIRONMENT', 'development')
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Remove default handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    if log_format == 'json' and environment == 'production':
        formatter = ProductionFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for production
    if environment == 'production':
        # Application logs
        app_file_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'quantumcertify.log'),
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=10,
            encoding='utf-8'
        )
        app_file_handler.setFormatter(formatter)
        app_file_handler.setLevel(getattr(logging, log_level, logging.INFO))
        root_logger.addHandler(app_file_handler)
        
        # Error logs (separate file for errors and above)
        error_file_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'quantumcertify_errors.log'),
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=5,
            encoding='utf-8'
        )
        error_file_handler.setFormatter(formatter)
        error_file_handler.setLevel(logging.ERROR)
        root_logger.addHandler(error_file_handler)
    
    # Security events logger
    security_logger = logging.getLogger('security')
    security_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'security.log'),
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=10,
        encoding='utf-8'
    )
    security_handler.setFormatter(formatter)
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)
    security_logger.propagate = False
    
    # Access logs logger
    if enable_access_logs:
        access_logger = logging.getLogger('access')
        access_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'access.log'),
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=10,
            encoding='utf-8'
        )
        access_handler.setFormatter(formatter)
        access_logger.addHandler(access_handler)
        access_logger.setLevel(logging.INFO)
        access_logger.propagate = False
    
    # Performance logger
    performance_logger = logging.getLogger('performance')
    performance_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'performance.log'),
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=5,
        encoding='utf-8'
    )
    performance_handler.setFormatter(formatter)
    performance_logger.addHandler(performance_handler)
    performance_logger.setLevel(logging.INFO)
    performance_logger.propagate = False
    
    # Suppress noisy third-party loggers in production
    if environment == 'production':
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('azure').setLevel(logging.WARNING)
        logging.getLogger('google').setLevel(logging.WARNING)
    
    # Log configuration startup
    logger = logging.getLogger(__name__)
    logger.info(
        "Production logging configured",
        extra={
            'extra_data': {
                'log_level': log_level,
                'log_format': log_format,
                'environment': environment,
                'enable_access_logs': enable_access_logs,
                'log_directory': log_dir
            }
        }
    )


class SecurityLogger:
    """
    Security-focused logger for tracking security events
    """
    
    def __init__(self):
        self.logger = logging.getLogger('security')
    
    def log_authentication_attempt(self, success: bool, user_id: str = None, 
                                 ip_address: str = None, user_agent: str = None):
        """Log authentication attempts"""
        self.logger.info(
            f"Authentication {'successful' if success else 'failed'}",
            extra={
                'extra_data': {
                    'event_type': 'authentication',
                    'success': success,
                    'user_id': user_id,
                    'ip_address': ip_address,
                    'user_agent': user_agent
                }
            }
        )
    
    def log_certificate_upload(self, file_name: str, file_size: int, 
                             ip_address: str = None, processing_time: float = None):
        """Log certificate upload events"""
        self.logger.info(
            "Certificate uploaded for analysis",
            extra={
                'extra_data': {
                    'event_type': 'certificate_upload',
                    'file_name': file_name,
                    'file_size': file_size,
                    'ip_address': ip_address,
                    'processing_time': processing_time
                }
            }
        )
    
    def log_security_violation(self, violation_type: str, details: str, 
                             ip_address: str = None, user_agent: str = None):
        """Log security violations"""
        self.logger.warning(
            f"Security violation detected: {violation_type}",
            extra={
                'extra_data': {
                    'event_type': 'security_violation',
                    'violation_type': violation_type,
                    'details': details,
                    'ip_address': ip_address,
                    'user_agent': user_agent
                }
            }
        )


class PerformanceLogger:
    """
    Performance monitoring logger
    """
    
    def __init__(self):
        self.logger = logging.getLogger('performance')
    
    def log_request_performance(self, endpoint: str, method: str, 
                              duration: float, status_code: int,
                              ip_address: str = None):
        """Log API request performance"""
        level = logging.WARNING if duration > 5.0 else logging.INFO
        
        self.logger.log(
            level,
            f"API request performance: {method} {endpoint}",
            extra={
                'extra_data': {
                    'event_type': 'api_performance',
                    'endpoint': endpoint,
                    'method': method,
                    'duration_seconds': duration,
                    'status_code': status_code,
                    'ip_address': ip_address,
                    'slow_request': duration > 5.0
                }
            }
        )
    
    def log_database_performance(self, operation: str, duration: float,
                               records_affected: int = None):
        """Log database operation performance"""
        level = logging.WARNING if duration > 2.0 else logging.INFO
        
        self.logger.log(
            level,
            f"Database operation performance: {operation}",
            extra={
                'extra_data': {
                    'event_type': 'database_performance',
                    'operation': operation,
                    'duration_seconds': duration,
                    'records_affected': records_affected,
                    'slow_query': duration > 2.0
                }
            }
        )


# Initialize loggers
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance
    """
    return logging.getLogger(name)