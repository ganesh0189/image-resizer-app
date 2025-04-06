import os
import psutil
import time
import threading
import shutil
from collections import deque

class SystemMonitor:
    def __init__(self):
        self.cpu_history = deque(maxlen=10)  # Last 10 CPU readings
        self.memory_history = deque(maxlen=10)  # Last 10 memory readings
        self.load_threshold = 80  # CPU load threshold (percentage)
        self.memory_threshold = 80  # Memory usage threshold (percentage)
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # Cleanup every 5 minutes
        self.monitoring = False
        self.lock = threading.Lock()
        
    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.monitoring:
            self.monitoring = True
            threading.Thread(target=self._monitor_resources, daemon=True).start()
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring = False
    
    def _monitor_resources(self):
        """Monitor system resources"""
        while self.monitoring:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_history.append(cpu_percent)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_history.append(memory_percent)
            
            # Check if cleanup is needed
            current_time = time.time()
            if current_time - self.last_cleanup > self.cleanup_interval:
                self._cleanup_old_files()
                self.last_cleanup = current_time
            
            # Sleep for a short time
            time.sleep(5)
    
    def _cleanup_old_files(self):
        """Clean up old files in the upload directory"""
        try:
            upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
            if os.path.exists(upload_dir):
                current_time = time.time()
                for filename in os.listdir(upload_dir):
                    file_path = os.path.join(upload_dir, filename)
                    # Check if file is older than 1 hour
                    if current_time - os.path.getmtime(file_path) > 3600:
                        try:
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                        except Exception as e:
                            print(f"Error cleaning up {file_path}: {e}")
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def get_system_status(self):
        """Get the current system status"""
        with self.lock:
            # Calculate average CPU usage
            avg_cpu = sum(self.cpu_history) / len(self.cpu_history) if self.cpu_history else 0
            
            # Calculate average memory usage
            avg_memory = sum(self.memory_history) / len(self.memory_history) if self.memory_history else 0
            
            # Determine system status
            status = "normal"
            if avg_cpu > self.load_threshold or avg_memory > self.memory_threshold:
                status = "busy"
            
            # Calculate estimated wait time (in seconds)
            wait_time = 0
            if status == "busy":
                # Rough estimate: 5 seconds per request in queue
                from app.queue_manager import queue_manager
                queue_length = len(queue_manager.queue)
                wait_time = queue_length * 5
            
            return {
                "status": status,
                "cpu_usage": round(avg_cpu, 1),
                "memory_usage": round(avg_memory, 1),
                "wait_time": wait_time,
                "queue_length": len(queue_manager.queue) if 'queue_manager' in locals() else 0
            }
    
    def is_system_busy(self):
        """Check if the system is busy"""
        status = self.get_system_status()
        return status["status"] == "busy"

# Create a global instance
system_monitor = SystemMonitor() 