// Status and queue management
let queueRequestId = null;
let statusCheckInterval = null;
let queueCheckInterval = null;

// Function to update the status indicator
function updateStatusIndicator(status) {
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    const waitTime = document.getElementById('wait-time');
    
    if (!statusIndicator || !statusText || !waitTime) return;
    
    if (status.status === 'busy') {
        statusIndicator.className = 'status-indicator busy';
        statusText.textContent = 'System Busy';
        
        if (status.wait_time > 0) {
            waitTime.textContent = `Estimated wait: ${Math.ceil(status.wait_time / 60)} minutes`;
            waitTime.style.display = 'block';
        } else {
            waitTime.style.display = 'none';
        }
    } else {
        statusIndicator.className = 'status-indicator normal';
        statusText.textContent = 'System Normal';
        waitTime.style.display = 'none';
    }
}

// Function to update the queue position
function updateQueuePosition(position) {
    const queuePosition = document.getElementById('queue-position');
    if (!queuePosition) return;
    
    if (position > 0) {
        queuePosition.textContent = `Your position in queue: ${position}`;
        queuePosition.style.display = 'block';
    } else {
        queuePosition.style.display = 'none';
    }
}

// Function to join the queue
async function joinQueue() {
    try {
        const response = await fetch('/api/queue/join', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            queueRequestId = data.request_id;
            updateQueuePosition(data.position);
            
            // Start checking queue position
            if (queueCheckInterval) clearInterval(queueCheckInterval);
            queueCheckInterval = setInterval(checkQueuePosition, 5000);
        } else {
            alert(data.error || 'Failed to join queue');
        }
    } catch (error) {
        console.error('Error joining queue:', error);
    }
}

// Function to check queue position
async function checkQueuePosition() {
    if (!queueRequestId) return;
    
    try {
        const response = await fetch(`/api/queue/position?request_id=${queueRequestId}`);
        const data = await response.json();
        
        if (response.ok) {
            updateQueuePosition(data.position);
            
            // If position is 0, we're no longer in the queue
            if (data.position === 0) {
                clearInterval(queueCheckInterval);
                queueCheckInterval = null;
            }
        }
    } catch (error) {
        console.error('Error checking queue position:', error);
    }
}

// Function to check system status
async function checkSystemStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (response.ok) {
            updateStatusIndicator(data);
        }
    } catch (error) {
        console.error('Error checking system status:', error);
    }
}

// Initialize status checking
document.addEventListener('DOMContentLoaded', function() {
    // Check status immediately
    checkSystemStatus();
    
    // Then check every 30 seconds
    if (statusCheckInterval) clearInterval(statusCheckInterval);
    statusCheckInterval = setInterval(checkSystemStatus, 30000);
    
    // Add event listener to form submission
    const form = document.getElementById('process-form');
    if (form) {
        form.addEventListener('submit', async function(e) {
            // Don't prevent default here, let the form submit normally
            // Just join the queue before submission
            await joinQueue();
        });
    }
}); 