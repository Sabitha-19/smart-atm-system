"""
ML Model Trainer for ATM Fraud Detection
Trains a Random Forest classifier to detect fraudulent transactions
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib
import os

class FraudDetectionModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'amount',
            'hour',
            'day_of_week',
            'transactions_today',
            'unique_locations_week',
            'time_since_last_transaction',
            'avg_amount_30days',
            'is_weekend'
        ]
    
    def train(self, data_path='data/atm_transactions.csv'):
        """
        Train the fraud detection model
        
        Args:
            data_path: Path to the training dataset CSV file
        """
        print("📚 Loading dataset...")
        df = pd.read_csv(data_path)
        
        # Prepare features and target
        X = df[self.feature_columns]
        y = df['is_fraud']
        
        print(f"📊 Dataset shape: {X.shape}")
        print(f"🔴 Fraud cases: {y.sum()} ({y.sum()/len(y)*100:.2f}%)")
        print(f"✅ Normal cases: {len(y) - y.sum()} ({(len(y) - y.sum())/len(y)*100:.2f}%)")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print("\n🔄 Scaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        print("\n🌳 Training Random Forest model...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            class_weight='balanced',  # Handle imbalanced data
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        print("\n📊 Evaluating model...")
        y_pred = self.model.predict(X_test_scaled)
        
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\n✅ Accuracy: {accuracy*100:.2f}%")
        
        print("\n📋 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['Normal', 'Fraud']))
        
        print("\n🎯 Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        print(f"\nTrue Negatives: {cm[0][0]}")
        print(f"False Positives: {cm[0][1]}")
        print(f"False Negatives: {cm[1][0]}")
        print(f"True Positives: {cm[1][1]}")
        
        # Feature importance
        print("\n🔑 Feature Importance:")
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        print(feature_importance)
        
        return accuracy
    
    def predict(self, transaction_data):
        """
        Predict if a transaction is fraudulent
        
        Args:
            transaction_data: Dictionary containing transaction features
            
        Returns:
            Dictionary with prediction and probability
        """
        # Convert to DataFrame
        df = pd.DataFrame([transaction_data])
        
        # Ensure all features are present
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0
        
        # Select and order features
        X = df[self.feature_columns]
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled)[0]
        probability = self.model.predict_proba(X_scaled)[0]
        
        return {
            'is_fraud': bool(prediction),
            'fraud_probability': float(probability[1]),
            'confidence': float(max(probability))
        }
    
    def save(self, model_path='models/fraud_detection_model.pkl', 
             scaler_path='models/scaler.pkl'):
        """Save the trained model and scaler"""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        print(f"\n💾 Model saved to: {model_path}")
        print(f"💾 Scaler saved to: {scaler_path}")
    
    def load(self, model_path='models/fraud_detection_model.pkl',
             scaler_path='models/scaler.pkl'):
        """Load a pre-trained model and scaler"""
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        print(f"✅ Model loaded from: {model_path}")
        print(f"✅ Scaler loaded from: {scaler_path}")

if __name__ == "__main__":
    print("🏦 ATM Fraud Detection Model Training\n")
    
    # Create and train model
    fraud_detector = FraudDetectionModel()
    accuracy = fraud_detector.train()
    
    # Save model
    fraud_detector.save()
    
    print("\n✅ Training completed successfully!")
    
    # Test with sample transactions
    print("\n🧪 Testing with sample transactions:")
    
    # Normal transaction
    normal_tx = {
        'amount': 150.0,
        'hour': 14,
        'day_of_week': 2,
        'transactions_today': 2,
        'unique_locations_week': 2,
        'time_since_last_transaction': 12.5,
        'avg_amount_30days': 200.0,
        'is_weekend': 0
    }
    
    result = fraud_detector.predict(normal_tx)
    print(f"\n✅ Normal Transaction:")
    print(f"   Amount: ${normal_tx['amount']}")
    print(f"   Fraud: {result['is_fraud']}")
    print(f"   Probability: {result['fraud_probability']*100:.2f}%")
    
    # Fraudulent transaction
    fraud_tx = {
        'amount': 2500.0,
        'hour': 2,
        'day_of_week': 3,
        'transactions_today': 12,
        'unique_locations_week': 8,
        'time_since_last_transaction': 0.5,
        'avg_amount_30days': 150.0,
        'is_weekend': 0
    }
    
    result = fraud_detector.predict(fraud_tx)
    print(f"\n🔴 Suspicious Transaction:")
    print(f"   Amount: ${fraud_tx['amount']}")
    print(f"   Fraud: {result['is_fraud']}")
    print(f"   Probability: {result['fraud_probability']*100:.2f}%")
