"""
Dataset Generator for ATM Fraud Detection
Generates synthetic transaction data with normal and fraudulent patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_dataset(num_samples=10000, fraud_ratio=0.1):
    """Generate synthetic ATM transaction dataset"""
    
    np.random.seed(42)
    random.seed(42)
    
    data = []
    num_fraud = int(num_samples * fraud_ratio)
    num_normal = num_samples - num_fraud
    
    # Generate normal transactions
    for i in range(num_normal):
        transaction = generate_normal_transaction(i)
        transaction['is_fraud'] = 0
        data.append(transaction)
    
    # Generate fraudulent transactions
    for i in range(num_fraud):
        transaction = generate_fraud_transaction(i + num_normal)
        transaction['is_fraud'] = 1
        data.append(transaction)
    
    # Create DataFrame and shuffle
    df = pd.DataFrame(data)
    df = df.sample(frac=1).reset_index(drop=True)
    
    return df

def generate_normal_transaction(transaction_id):
    """Generate a normal transaction with typical patterns"""
    
    # Normal transaction characteristics
    amount = np.random.choice([
        np.random.uniform(20, 200),      # Small withdrawals (70%)
        np.random.uniform(200, 500),     # Medium withdrawals (20%)
        np.random.uniform(500, 1000)     # Large withdrawals (10%)
    ], p=[0.7, 0.2, 0.1])
    
    # Normal transaction times (mostly business hours)
    hour = np.random.choice(range(24), p=get_normal_hour_distribution())
    
    # Typical transaction frequency (1-5 per day)
    transactions_today = np.random.randint(1, 6)
    
    # Normal locations (usually 1-3 locations)
    unique_locations = np.random.randint(1, 4)
    
    # Time since last transaction (normal pattern)
    time_since_last = np.random.uniform(3, 48)  # 3-48 hours
    
    # Average spending
    avg_amount = np.random.uniform(100, 400)
    
    return {
        'transaction_id': transaction_id,
        'amount': round(amount, 2),
        'hour': hour,
        'day_of_week': np.random.randint(0, 7),
        'transactions_today': transactions_today,
        'unique_locations_week': unique_locations,
        'time_since_last_transaction': round(time_since_last, 2),
        'avg_amount_30days': round(avg_amount, 2),
        'is_weekend': 1 if np.random.rand() > 0.7 else 0
    }

def generate_fraud_transaction(transaction_id):
    """Generate a fraudulent transaction with suspicious patterns"""
    
    # Fraudulent transaction characteristics
    fraud_type = np.random.choice(['high_amount', 'high_frequency', 'unusual_time', 'mixed'])
    
    if fraud_type == 'high_amount':
        amount = np.random.uniform(1000, 5000)
        transactions_today = np.random.randint(1, 4)
        hour = np.random.randint(0, 24)
    elif fraud_type == 'high_frequency':
        amount = np.random.uniform(200, 800)
        transactions_today = np.random.randint(8, 20)
        hour = np.random.randint(0, 24)
    elif fraud_type == 'unusual_time':
        amount = np.random.uniform(300, 1500)
        transactions_today = np.random.randint(3, 8)
        hour = np.random.choice([0, 1, 2, 3, 4, 22, 23])
    else:  # mixed patterns
        amount = np.random.uniform(800, 3000)
        transactions_today = np.random.randint(6, 15)
        hour = np.random.choice([0, 1, 2, 3, 22, 23])
    
    unique_locations = np.random.randint(5, 15)
    time_since_last = np.random.uniform(0.1, 2)
    avg_amount = np.random.uniform(50, 300)
    
    return {
        'transaction_id': transaction_id,
        'amount': round(amount, 2),
        'hour': hour,
        'day_of_week': np.random.randint(0, 7),
        'transactions_today': transactions_today,
        'unique_locations_week': unique_locations,
        'time_since_last_transaction': round(time_since_last, 2),
        'avg_amount_30days': round(avg_amount, 2),
        'is_weekend': 1 if np.random.rand() > 0.5 else 0
    }

def get_normal_hour_distribution():
    """Return probability distribution for transaction hours"""
    probs = np.array([
        0.01, 0.01, 0.01, 0.01, 0.01, 0.01,
        0.02, 0.03, 0.05, 0.07, 0.08, 0.09,
        0.10, 0.09, 0.08, 0.07, 0.06, 0.06,
        0.05, 0.04, 0.03, 0.02, 0.01, 0.01
    ])
    return probs / probs.sum()

if __name__ == "__main__":
    print("🏦 Generating ATM Transaction Dataset...")
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate dataset
    df = generate_dataset(num_samples=10000, fraud_ratio=0.1)
    
    # Save to CSV
    output_path = 'data/atm_transactions.csv'
    df.to_csv(output_path, index=False)
    
    print(f"✅ Dataset generated successfully!")
    print(f"📊 Total transactions: {len(df)}")
    print(f"✅ Normal transactions: {len(df[df['is_fraud'] == 0])}")
    print(f"🔴 Fraudulent transactions: {len(df[df['is_fraud'] == 1])}")
    print(f"💾 Saved to: {output_path}")
    
    print("\n📈 Dataset Statistics:")
    print(df.describe())
    
    print("\n🔍 Feature Correlation with Fraud:")
    print(df.corr()['is_fraud'].sort_values(ascending=False))
