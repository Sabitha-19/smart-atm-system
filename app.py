"""
Smart ATM System with ML-based Fraud Detection
Flask application for ATM operations and admin dashboard
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
import os
import sys

# Import custom modules
from database import Database
from train_model import FraudDetectionModel

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Initialize database
db = Database()

# Initialize fraud detection model
fraud_detector = FraudDetectionModel()

# Load pre-trained model if exists
model_path = 'models/fraud_detection_model.pkl'
if os.path.exists(model_path):
    try:
        fraud_detector.load()
        print("✅ Fraud detection model loaded successfully")
    except Exception as e:
        print(f"⚠️ Could not load model: {e}")
        print("Please run 'python generate_dataset.py' and 'python train_model.py' first")
else:
    print("⚠️ Model not found. Please run training scripts first.")

# ==================== User Routes ====================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        account_number = request.form.get('account_number')
        pin = request.form.get('pin')
        
        user = db.verify_user(account_number, pin)
        
        if user:
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            session['account_number'] = user['account_number']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid account number or PIN')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.get_user(session['user_id'])
    transactions = db.get_user_transactions(session['user_id'], limit=5)
    
    return render_template('dashboard.html', user=user, transactions=transactions)

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

# ==================== Transaction Routes ====================

@app.route('/check_balance')
def check_balance():
    """Get current balance"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    user = db.get_user(session['user_id'])
    return jsonify({'success': True, 'balance': user['balance']})

@app.route('/withdraw', methods=['POST'])
def withdraw():
    """Process withdrawal transaction"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    try:
        amount = float(request.json.get('amount', 0))
        
        if amount <= 0:
            return jsonify({'success': False, 'error': 'Invalid amount'})
        
        user = db.get_user(session['user_id'])
        
        if user['balance'] < amount:
            return jsonify({'success': False, 'error': 'Insufficient balance'})
        
        # Get transaction stats for fraud detection
        stats = db.get_transaction_stats(session['user_id'])
        
        # Prepare transaction data for fraud detection
        now = datetime.now()
        transaction_data = {
            'amount': amount,
            'hour': now.hour,
            'day_of_week': now.weekday(),
            'transactions_today': stats['transactions_today'],
            'unique_locations_week': stats['unique_locations_week'],
            'time_since_last_transaction': stats['time_since_last_transaction'],
            'avg_amount_30days': stats['avg_amount_30days'],
            'is_weekend': 1 if now.weekday() >= 5 else 0
        }
        
        # Check for fraud
        fraud_result = fraud_detector.predict(transaction_data)
        is_fraud = fraud_result['is_fraud']
        fraud_score = fraud_result['fraud_probability']
        
        # If fraud detected, block transaction
        if is_fraud:
            # Log blocked transaction
            db.add_transaction(
                session['user_id'],
                'withdrawal',
                amount,
                user['balance'],
                is_fraud=True,
                fraud_score=fraud_score,
                status='blocked'
            )
            
            # Create fraud alert
            db.add_fraud_alert(
                session['user_id'],
                None,
                'suspicious_withdrawal',
                f'Suspicious withdrawal of ${amount:.2f} detected. Fraud probability: {fraud_score*100:.1f}%',
                severity='high'
            )
            
            return jsonify({
                'success': False,
                'error': 'Transaction blocked due to suspicious activity. Please contact support.',
                'is_fraud': True
            })
        
        # Process transaction
        new_balance = user['balance'] - amount
        db.update_balance(session['user_id'], new_balance)
        
        # Log transaction
        db.add_transaction(
            session['user_id'],
            'withdrawal',
            amount,
            new_balance,
            is_fraud=False,
            fraud_score=fraud_score
        )
        
        return jsonify({
            'success': True,
            'amount': amount,
            'new_balance': new_balance,
            'is_fraud': False,
            'fraud_score': fraud_score
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/deposit', methods=['POST'])
def deposit():
    """Process deposit transaction"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    try:
        amount = float(request.json.get('amount', 0))
        
        if amount <= 0:
            return jsonify({'success': False, 'error': 'Invalid amount'})
        
        user = db.get_user(session['user_id'])
        
        # Get transaction stats
        stats = db.get_transaction_stats(session['user_id'])
        
        # Prepare transaction data for fraud detection
        now = datetime.now()
        transaction_data = {
            'amount': amount,
            'hour': now.hour,
            'day_of_week': now.weekday(),
            'transactions_today': stats['transactions_today'],
            'unique_locations_week': stats['unique_locations_week'],
            'time_since_last_transaction': stats['time_since_last_transaction'],
            'avg_amount_30days': stats['avg_amount_30days'],
            'is_weekend': 1 if now.weekday() >= 5 else 0
        }
        
        # Check for fraud (even for deposits)
        fraud_result = fraud_detector.predict(transaction_data)
        fraud_score = fraud_result['fraud_probability']
        
        # Process transaction
        new_balance = user['balance'] + amount
        db.update_balance(session['user_id'], new_balance)
        
        # Log transaction
        db.add_transaction(
            session['user_id'],
            'deposit',
            amount,
            new_balance,
            is_fraud=False,
            fraud_score=fraud_score
        )
        
        return jsonify({
            'success': True,
            'amount': amount,
            'new_balance': new_balance
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/mini_statement')
def mini_statement():
    """Get mini statement"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    transactions = db.get_user_transactions(session['user_id'], limit=10)
    
    # Format transactions
    formatted_transactions = []
    for tx in transactions:
        formatted_transactions.append({
            'type': tx['transaction_type'],
            'amount': tx['amount'],
            'balance': tx['balance_after'],
            'date': tx['timestamp'],
            'status': tx['status']
        })
    
    return jsonify({
        'success': True,
        'transactions': formatted_transactions
    })

# ==================== Admin Routes ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = db.verify_admin(username, password)
        
        if admin:
            session['admin_id'] = admin['admin_id']
            session['admin_username'] = admin['username']
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    users = db.get_all_users()
    alerts = db.get_fraud_alerts(resolved=False)
    transactions = db.get_all_transactions(limit=20)
    
    # Calculate statistics
    total_users = len(users)
    flagged_users = sum(1 for u in users if u['is_flagged'])
    blocked_users = sum(1 for u in users if u['is_blocked'])
    active_alerts = len(alerts)
    
    stats = {
        'total_users': total_users,
        'flagged_users': flagged_users,
        'blocked_users': blocked_users,
        'active_alerts': active_alerts
    }
    
    return render_template(
        'admin_dashboard.html',
        users=users,
        alerts=alerts,
        transactions=transactions,
        stats=stats
    )

@app.route('/admin/logout')
def admin_logout():
    """Logout admin"""
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/block_user/<int:user_id>')
def block_user(user_id):
    """Block a user"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'error': 'Not authorized'})
    
    db.block_user(user_id)
    return jsonify({'success': True})

@app.route('/admin/unblock_user/<int:user_id>')
def unblock_user(user_id):
    """Unblock a user"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'error': 'Not authorized'})
    
    db.unblock_user(user_id)
    return jsonify({'success': True})

# ==================== API Routes ====================

@app.route('/api/stats')
def api_stats():
    """Get system statistics for charts"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'error': 'Not authorized'})
    
    transactions = db.get_all_transactions(limit=100)
    
    # Transactions by hour
    hourly_counts = [0] * 24
    for tx in transactions:
        hour = datetime.fromisoformat(tx['timestamp']).hour
        hourly_counts[hour] += 1
    
    # Fraud vs Normal
    fraud_count = sum(1 for tx in transactions if tx['is_fraud'])
    normal_count = len(transactions) - fraud_count
    
    return jsonify({
        'success': True,
        'hourly_transactions': hourly_counts,
        'fraud_count': fraud_count,
        'normal_count': normal_count
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏦 Smart ATM System with Fraud Detection")
    print("="*60)
    print("\n📋 Sample User Accounts:")
    print("   Account: 1234567890, PIN: 1234, Balance: $5000")
    print("   Account: 0987654321, PIN: 5678, Balance: $3000")
    print("   Account: 1111222233, PIN: 9999, Balance: $7500")
    print("   Account: 4444555566, PIN: 0000, Balance: $2000")
    print("\n🔑 Admin Login:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n🌐 Starting server at http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
