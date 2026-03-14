// User Dashboard JavaScript

function showWithdraw() {
    document.getElementById('withdrawModal').style.display = 'block';
    document.getElementById('withdrawAmount').focus();
}

function showDeposit() {
    document.getElementById('depositModal').style.display = 'block';
    document.getElementById('depositAmount').focus();
}

function showMiniStatement() {
    fetch('/mini_statement')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayMiniStatement(data.transactions);
                document.getElementById('statementModal').style.display = 'block';
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to fetch mini statement');
        });
}

function displayMiniStatement(transactions) {
    const content = document.getElementById('statementContent');
    
    if (transactions.length === 0) {
        content.innerHTML = '<p class="no-transactions">No transactions found</p>';
        return;
    }
    
    let html = '<div class="transactions-list">';
    transactions.forEach(tx => {
        const sign = tx.type === 'withdrawal' ? '-' : '+';
        const amountClass = tx.type === 'withdrawal' ? 'negative' : 'positive';
        const statusBadge = tx.status === 'blocked' ? '<span class="status-badge blocked">BLOCKED</span>' : '';
        
        html += `
            <div class="transaction-item">
                <div class="tx-info">
                    <span class="tx-type">${tx.type.charAt(0).toUpperCase() + tx.type.slice(1)}</span>
                    <span class="tx-date">${tx.date}</span>
                </div>
                <div class="tx-amount ${amountClass}">
                    ${sign}$${tx.amount.toFixed(2)}
                </div>
                ${statusBadge}
            </div>
        `;
    });
    html += '</div>';
    
    content.innerHTML = html;
}

function checkBalance() {
    fetch('/check_balance')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`Your current balance is: $${data.balance.toFixed(2)}`);
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to check balance');
        });
}

function processWithdraw() {
    const amount = parseFloat(document.getElementById('withdrawAmount').value);
    
    if (!amount || amount <= 0) {
        alert('Please enter a valid amount');
        return;
    }
    
    fetch('/withdraw', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ amount: amount })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateBalance(data.new_balance);
            closeModal('withdrawModal');
            document.getElementById('withdrawAmount').value = '';
            alert(`Withdrawal successful!\nAmount: $${data.amount.toFixed(2)}\nNew Balance: $${data.new_balance.toFixed(2)}`);
            setTimeout(() => location.reload(), 1500);
        } else {
            if (data.is_fraud) {
                alert('⚠️ FRAUD ALERT!\n\n' + data.error + '\n\nThis transaction has been blocked for your security.');
            } else {
                alert('Error: ' + data.error);
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Transaction failed. Please try again.');
    });
}

function processDeposit() {
    const amount = parseFloat(document.getElementById('depositAmount').value);
    
    if (!amount || amount <= 0) {
        alert('Please enter a valid amount');
        return;
    }
    
    fetch('/deposit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ amount: amount })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateBalance(data.new_balance);
            closeModal('depositModal');
            document.getElementById('depositAmount').value = '';
            alert(`Deposit successful!\nAmount: $${data.amount.toFixed(2)}\nNew Balance: $${data.new_balance.toFixed(2)}`);
            setTimeout(() => location.reload(), 1500);
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Transaction failed. Please try again.');
    });
}

function updateBalance(newBalance) {
    document.getElementById('balance-display').textContent = `$${newBalance.toFixed(2)}`;
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// Handle Enter key in input fields
document.addEventListener('DOMContentLoaded', function() {
    const withdrawInput = document.getElementById('withdrawAmount');
    const depositInput = document.getElementById('depositAmount');
    
    if (withdrawInput) {
        withdrawInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                processWithdraw();
            }
        });
    }
    
    if (depositInput) {
        depositInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                processDeposit();
            }
        });
    }
});
