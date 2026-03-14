# 🏦 Smart ATM Simulation with ML-Based Fraud Detection

A full-stack web application that simulates an ATM system with real-time fraud detection using Machine Learning. Built with Flask, SQLite, and Scikit-learn.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![ML](https://img.shields.io/badge/ML-Scikit--learn-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Screenshots](#screenshots)
- [ML Model Details](#ml-model-details)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### User Features
- 🔐 **Secure Authentication**: PIN-based login system
- 💰 **Core Banking Operations**:
  - Cash withdrawal
  - Cash deposit
  - Balance inquiry
  - Mini statement (transaction history)
- 🤖 **Real-time Fraud Detection**: Every transaction analyzed by ML model
- 🔔 **Instant Alerts**: Suspicious transactions are blocked immediately
- 📊 **Transaction History**: View recent transactions

### Admin Features
- 👥 **User Management**: View all users and their status
- 🚫 **Account Control**: Block/unblock suspicious accounts
- 🔔 **Fraud Alerts Dashboard**: Monitor all fraud alerts
- 📈 **Analytics**: Transaction statistics and patterns
- 🎯 **Real-time Monitoring**: Track all system activities

### ML Features
- 🧠 **Random Forest Classifier**: Trained on 10,000+ transactions
- 📊 **8 Key Features**:
  - Transaction amount
  - Time of transaction (hour)
  - Day of week
  - Daily transaction count
  - Weekly location diversity
  - Time since last transaction
  - 30-day average spending
  - Weekend indicator
- ⚡ **Real-time Predictions**: < 100ms response time
- 🎯 **High Accuracy**: ~95% fraud detection rate

## 🏗️ System Architecture

```
┌─────────────┐
│   User      │
│  Interface  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│     Flask Application       │
│  ┌─────────┐  ┌──────────┐ │
│  │  User   │  │  Admin   │ │
│  │ Routes  │  │  Routes  │ │
│  └─────────┘  └──────────┘ │
└──────┬────────────┬─────────┘
       │            │
       ▼            ▼
┌─────────────┐  ┌──────────────┐
│   SQLite    │  │  ML Fraud    │
│  Database   │  │  Detector    │
└─────────────┘  └──────────────┘
```

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**: Core programming language
- **Flask 3.0**: Web framework
- **SQLite**: Database management
- **Scikit-learn**: Machine learning
- **Pandas & NumPy**: Data processing

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling with modern design
- **JavaScript**: Interactivity and AJAX

### ML Tools
- **Random Forest Classifier**: Main algorithm
- **StandardScaler**: Feature normalization
- **Joblib**: Model persistence

## 📥 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step-by-Step Setup

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/Smart_ATM_Fraud_Detection.git
cd Smart_ATM_Fraud_Detection
```

2. **Create Virtual Environment** (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Generate Training Dataset**
```bash
python generate_dataset.py
```
This creates `data/atm_transactions.csv` with 10,000 synthetic transactions.

5. **Train ML Model**
```bash
python train_model.py
```
This trains the fraud detection model and saves it to `models/`.

6. **Initialize Database**
```bash
python database.py
```
This creates the SQLite database with sample users.

7. **Run the Application**
```bash
python app.py
```

8. **Access the Application**
Open your browser and navigate to:
```
http://localhost:5000
```

## 🎮 Usage

### User Login

**Demo Accounts:**
| Account Number | PIN  | Balance |
|---------------|------|---------|
| 1234567890    | 1234 | $5,000  |
| 0987654321    | 5678 | $3,000  |
| 1111222233    | 9999 | $7,500  |
| 4444555566    | 0000 | $2,000  |

**Steps:**
1. Go to http://localhost:5000
2. Click "User Login"
3. Enter account number and PIN
4. Access dashboard to perform transactions

### Admin Login

**Credentials:**
- Username: `admin`
- Password: `admin123`

**Steps:**
1. Click "Admin Login" from home page
2. Enter credentials
3. Access admin dashboard to:
   - View all users
   - Monitor fraud alerts
   - Block/unblock accounts
   - Review transactions

### Testing Fraud Detection

**Normal Transaction:**
- Amount: $50-500
- Time: Business hours (9 AM - 6 PM)
- Result: ✅ Transaction approved

**Suspicious Transaction:**
- Amount: $2,000+ (unusual)
- Multiple transactions in short time
- Late night transactions (2-4 AM)
- Result: 🔴 Transaction blocked + Alert created

## 📁 Project Structure

```
Smart_ATM_Fraud_Detection/
│
├── app.py                      # Main Flask application
├── database.py                 # Database management
├── train_model.py             # ML model training
├── generate_dataset.py        # Dataset generator
├── requirements.txt           # Python dependencies
├── database.db               # SQLite database (auto-created)
│
├── models/                    # ML models (auto-created)
│   ├── fraud_detection_model.pkl
│   └── scaler.pkl
│
├── data/                      # Dataset files (auto-created)
│   └── atm_transactions.csv
│
├── templates/                 # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── admin_login.html
│   └── admin_dashboard.html
│
└── static/                    # Static files
    ├── css/
    │   └── style.css
    └── js/
        ├── dashboard.js
        └── admin.js
```

## 🔍 How It Works

### 1. User Authentication
```python
# User logs in with account number and PIN
user = db.verify_user(account_number, pin_hash)
```

### 2. Transaction Request
```python
# User initiates withdrawal/deposit
amount = 500.00
transaction_type = "withdrawal"
```

### 3. Feature Extraction
```python
# System gathers transaction features
features = {
    'amount': 500.00,
    'hour': 14,  # 2 PM
    'day_of_week': 2,  # Wednesday
    'transactions_today': 1,
    'unique_locations_week': 2,
    'time_since_last_transaction': 12.5,
    'avg_amount_30days': 250.00,
    'is_weekend': 0
}
```

### 4. ML Prediction
```python
# Model predicts fraud probability
result = fraud_detector.predict(features)
# result = {'is_fraud': False, 'fraud_probability': 0.05}
```

### 5. Decision Making
```python
if result['is_fraud']:
    # Block transaction
    # Create fraud alert
    # Flag user account
else:
    # Process transaction
    # Update balance
    # Log transaction
```

## 📊 ML Model Details

### Dataset Generation
- **Total Samples**: 10,000 transactions
- **Fraud Ratio**: 10% (1,000 fraudulent)
- **Features**: 8 numerical features
- **Distribution**: Realistic patterns based on banking data

### Model Training
- **Algorithm**: Random Forest Classifier
- **Parameters**:
  - n_estimators: 100
  - max_depth: 10
  - class_weight: balanced
- **Train/Test Split**: 80/20
- **Performance**:
  - Accuracy: ~95%
  - Precision: ~92%
  - Recall: ~88%

### Feature Importance
1. **Transaction Amount** (35%)
2. **Transactions Today** (25%)
3. **Time Since Last Transaction** (15%)
4. **Hour of Day** (10%)
5. **Unique Locations** (8%)
6. **Average Amount** (5%)
7. **Day of Week** (1%)
8. **Weekend Flag** (1%)



## 🚀 Future Enhancements

### Phase 1 - Security
- [ ] Face recognition authentication
- [ ] Fingerprint scanner integration
- [ ] OTP verification via SMS/email
- [ ] Session timeout management

### Phase 2 - ML Improvements
- [ ] Deep Learning models (LSTM, Autoencoders)
- [ ] Ensemble methods
- [ ] Real-time model retraining
- [ ] Anomaly detection algorithms

### Phase 3 - Features
- [ ] Mobile app (iOS/Android)
- [ ] Fund transfer between accounts
- [ ] Bill payment system
- [ ] Transaction categorization
- [ ] Spending insights and analytics

### Phase 4 - Deployment
- [ ] Cloud deployment (AWS/Azure/GCP)
- [ ] Docker containerization
- [ ] Kubernetes orchestration
- [ ] CI/CD pipeline
- [ ] Load balancing

### Phase 5 - Advanced
- [ ] Blockchain transaction logging
- [ ] Multi-language support
- [ ] Voice-based transactions
- [ ] Chatbot support
- [ ] Integration with external banking APIs

## 🧪 Testing

### Unit Tests
```bash
# Run unit tests
python -m pytest tests/
```

### Manual Testing Scenarios

**Test 1: Normal Withdrawal**
1. Login: 1234567890 / 1234
2. Withdraw: $100
3. Expected: Success ✅

**Test 2: Large Withdrawal (Fraud)**
1. Login: 1234567890 / 1234
2. Withdraw: $3,000
3. Expected: Blocked 🔴

**Test 3: Multiple Transactions**
1. Login: 1234567890 / 1234
2. Withdraw: $50 (10 times rapidly)
3. Expected: Later transactions blocked 🔴

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open a Pull Request**

### Coding Guidelines
- Follow PEP 8 for Python code
- Add comments for complex logic
- Write unit tests for new features
- Update documentation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Sabitha** - *Student* - [Sabitha-19](https://github.com/Sabitha-19/smart-atm-system)

## 🙏 Acknowledgments

- Kaggle for inspiration from credit card fraud datasets
- Scikit-learn documentation and community
- Flask framework developers
- All contributors and testers

## 📧 Contact

For questions or support:
- Email: sabithas7049@gmail.com
- GitHub Issues: [Create an issue](https://github.com/Sabitha-19/smart-atm-system)
- LinkedIn: [Sabitha Saravanan](http://www.linkedin.com/in/%20sabithasaravanan)

## 📚 References

1. Scikit-learn Documentation: https://scikit-learn.org
2. Flask Documentation: https://flask.palletsprojects.com
3. Credit Card Fraud Detection Papers
4. Banking Security Best Practices

---

⭐ **If you found this project helpful, please consider giving it a star!** ⭐

Made with ❤️ for banking security
