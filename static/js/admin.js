// Admin Dashboard JavaScript

function showTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

function blockUser(userId) {
    if (!confirm('Are you sure you want to block this user?')) {
        return;
    }
    
    fetch(`/admin/block_user/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('User blocked successfully');
                location.reload();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to block user');
        });
}

function unblockUser(userId) {
    if (!confirm('Are you sure you want to unblock this user?')) {
        return;
    }
    
    fetch(`/admin/unblock_user/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('User unblocked successfully');
                location.reload();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to unblock user');
        });
}

// Load statistics for charts (optional enhancement)
function loadStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('System statistics:', data);
                // You can add chart visualization here using Chart.js or similar
            }
        })
        .catch(error => {
            console.error('Error loading stats:', error);
        });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load stats if needed
    // loadStats();
});
