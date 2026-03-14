# Quick Setup Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Python
Make sure you have Python 3.8 or higher installed:
```bash
python --version
```

### Step 2: Clone & Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/Smart_ATM_Fraud_Detection.git
cd Smart_ATM_Fraud_Detection

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Initialize System
```bash
# Generate training data
python generate_dataset.py

# Train the ML model
python train_model.py

# Initialize database
python database.py
```

### Step 4: Run Application
```bash
python app.py
```

Visit: http://localhost:5000

## 🎯 Quick Test

### User Login
- Account: `1234567890`
- PIN: `1234`
- Try withdrawing $100 (✅ should work)
- Try withdrawing $3000 (🔴 should be blocked)

### Admin Login
- Username: `admin`
- Password: `admin123`
- View fraud alerts and user management

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

### Module Not Found
```bash
pip install -r requirements.txt --upgrade
```

### Database Locked
```bash
# Delete and reinitialize
rm database.db
python database.py
```

## 📋 Testing Fraud Detection

| Scenario | Amount | Time | Expected Result |
|----------|--------|------|----------------|
| Normal | $100 | 2 PM | ✅ Approved |
| High Amount | $2500 | 2 PM | 🔴 Blocked |
| Late Night | $500 | 2 AM | 🔴 Blocked |
| Multiple TX | $200 x 10 | Rapid | 🔴 Later blocked |

## 🆘 Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Open an issue on GitHub
- Review the code comments

## 📝 Notes

- Default admin credentials are for demo only
- Sample users have virtual money for testing
- All transactions are stored in SQLite database
- ML model can be retrained with new data

Happy Testing! 🎉
