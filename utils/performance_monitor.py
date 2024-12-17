import psutil
import time
from collections import deque
from utils.config import config
from utils.logger import setup_logger

class PerformanceMonitor:
    def __init__(self):
        self.logger = setup_logger("performance_monitor")
        self.execution_times = deque(maxlen=1000)
        self.process = psutil.Process()
        self.start_time = time.time()

    def record_execution(self, execution_time: float):
        """Record execution time in milliseconds"""
        self.execution_times.append(execution_time)
        
        if execution_time > config.MIN_EXECUTION_SPEED_MS:
            self.logger.warning(
                f"Slow execution detected: {execution_time:.2f}ms"
            )

    def check_system_resources(self):
        """Monitor system resources"""
        memory_usage = self.process.memory_info().rss / 1024 / 1024  # MB
        cpu_percent = self.process.cpu_percent()
        
        if memory_usage > config.MEMORY_LIMIT_MB:
            self.logger.warning(
                f"High memory usage: {memory_usage:.2f}MB"
            )
            
        return {
            'memory_usage_mb': memory_usage,
            'cpu_percent': cpu_percent,
            'avg_execution_ms': sum(self.execution_times)/len(self.execution_times) if self.execution_times else 0,
            'uptime_seconds': time.time() - self.start_time
        }

    def get_performance_metrics(self):
        """Get all performance metrics"""
        metrics = self.check_system_resources()
        
        return {
            **metrics,
            'execution_times_95th': sorted(self.execution_times)[int(len(self.execution_times)*0.95)] if self.execution_times else 0,
            'total_executions': len(self.execution_times)
        } 