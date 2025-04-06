import time
import threading
from collections import deque
import uuid
import os

class QueueManager:
    def __init__(self):
        self.queue = deque()
        self.processing = False
        self.lock = threading.Lock()
        self.request_times = {}  # Track request times for rate limiting
        self.cache = {}  # Cache for processed images
        self.cache_expiry = 3600  # Cache expiry in seconds (1 hour)
        self.rate_limit = 10  # Max requests per minute per IP
        self.rate_window = 60  # Rate limit window in seconds
        
    def add_to_queue(self, request_id, ip_address):
        """Add a request to the queue and return its position"""
        with self.lock:
            # Check rate limiting
            if not self._check_rate_limit(ip_address):
                return -1, "Rate limit exceeded. Please try again later."
            
            # Add to queue
            self.queue.append((request_id, time.time()))
            position = len(self.queue)
            
            # Start processing if not already running
            if not self.processing:
                self._start_processing()
                
            return position, None
    
    def _check_rate_limit(self, ip_address):
        """Check if the IP has exceeded the rate limit"""
        current_time = time.time()
        
        # Clean up old requests
        self.request_times = {ip: times for ip, times in self.request_times.items() 
                             if any(t > current_time - self.rate_window for t in times)}
        
        # Initialize or get existing requests for this IP
        if ip_address not in self.request_times:
            self.request_times[ip_address] = []
        
        # Check if rate limit is exceeded
        if len(self.request_times[ip_address]) >= self.rate_limit:
            return False
        
        # Add current request time
        self.request_times[ip_address].append(current_time)
        return True
    
    def _start_processing(self):
        """Start processing the queue"""
        self.processing = True
        threading.Thread(target=self._process_queue, daemon=True).start()
    
    def _process_queue(self):
        """Process items in the queue"""
        while True:
            with self.lock:
                if not self.queue:
                    self.processing = False
                    break
                
                request_id, _ = self.queue.popleft()
            
            # Process the request (actual processing happens in the route)
            time.sleep(0.1)  # Small delay to prevent CPU hogging
    
    def get_queue_position(self, request_id):
        """Get the position of a request in the queue"""
        with self.lock:
            for i, (req_id, _) in enumerate(self.queue):
                if req_id == request_id:
                    return i + 1
            return 0  # Not in queue (either processed or not found)
    
    def add_to_cache(self, cache_key, result):
        """Add a processed result to the cache"""
        with self.lock:
            self.cache[cache_key] = {
                'result': result,
                'timestamp': time.time()
            }
    
    def get_from_cache(self, cache_key):
        """Get a result from the cache if it exists and is not expired"""
        with self.lock:
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry['timestamp'] < self.cache_expiry:
                    return cache_entry['result']
                else:
                    # Remove expired cache entry
                    del self.cache[cache_key]
            return None
    
    def cleanup_old_files(self, file_paths, max_age=3600):
        """Clean up old processed files"""
        current_time = time.time()
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age:
                        os.remove(file_path)
            except Exception:
                pass  # Ignore errors during cleanup

# Create a global instance
queue_manager = QueueManager() 