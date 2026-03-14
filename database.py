"""
Database module for ATM system
Handles user accounts, transactions, and fraud alerts
"""

import sqlite3
from datetime import datetime
import hashlib


class Database:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Create and return database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def hash_pin(self, pin):
        """Hash PIN for secure storage"""
        return hashlib.sha256(pin.encode()).hexdigest()

    def init_database(self):
        """Create tables if they do not exist"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # USERS TABLE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT UNIQUE NOT NULL,
            pin_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            balance REAL DEFAULT 1000.0,
            is_blocked INTEGER DEFAULT 0,
            is_flagged INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # TRANSACTIONS TABLE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            balance_after REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            location TEXT DEFAULT 'ATM-001',
            is_fraud INTEGER DEFAULT 0,
            fraud_score REAL DEFAULT 0.0,
            status TEXT DEFAULT 'completed',
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)

        # FRAUD ALERT TABLE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fraud_alerts (
            alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            transaction_id INTEGER,
            alert_type TEXT NOT NULL,
            description TEXT,
            severity TEXT DEFAULT 'medium',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_resolved INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
        )
        """)

        # ADMIN TABLE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()

        # Default admin
        cursor.execute("SELECT * FROM admins WHERE username=?", ("admin",))
        if not cursor.fetchone():
            password_hash = self.hash_pin("admin123")
            cursor.execute(
                "INSERT INTO admins (username,password_hash) VALUES (?,?)",
                ("admin", password_hash)
            )
            conn.commit()
            print("✅ Default admin created (admin / admin123)")

        # Create sample users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        if cursor.fetchone()["count"] == 0:
            self.create_sample_users(cursor)
            conn.commit()
            print("✅ Sample users created")

        conn.close()

    def create_sample_users(self, cursor):
        """Insert demo users"""
        users = [
            ("1234567890", "1234", "John Doe", 5000),
            ("0987654321", "5678", "Jane Smith", 3000),
            ("1111222233", "9999", "Bob Johnson", 7500),
            ("4444555566", "0000", "Alice Williams", 2000),
        ]

        for acc, pin, name, balance in users:
            pin_hash = self.hash_pin(pin)

            cursor.execute("""
            INSERT INTO users (account_number,pin_hash,name,balance)
            VALUES (?,?,?,?)
            """, (acc, pin_hash, name, balance))

    def verify_user(self, account_number, pin):
        """Check login credentials"""
        conn = self.get_connection()
        cursor = conn.cursor()

        pin_hash = self.hash_pin(pin)

        cursor.execute("""
        SELECT * FROM users
        WHERE account_number=? AND pin_hash=? AND is_blocked=0
        """, (account_number, pin_hash))

        user = cursor.fetchone()
        conn.close()

        if user:
            return dict(user)
        return None

    def verify_admin(self, username, password):
        """Admin login"""
        conn = self.get_connection()
        cursor = conn.cursor()

        password_hash = self.hash_pin(password)

        cursor.execute("""
        SELECT * FROM admins
        WHERE username=? AND password_hash=?
        """, (username, password_hash))

        admin = cursor.fetchone()
        conn.close()

        if admin:
            return dict(admin)
        return None

    def get_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user = cursor.fetchone()

        conn.close()

        return dict(user) if user else None

    def update_balance(self, user_id, new_balance):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET balance=? WHERE user_id=?",
            (new_balance, user_id)
        )

        conn.commit()
        conn.close()

    def add_transaction(self, user_id, transaction_type, amount, balance_after,
                        is_fraud=False, fraud_score=0.0):

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO transactions
        (user_id,transaction_type,amount,balance_after,is_fraud,fraud_score)
        VALUES (?,?,?,?,?,?)
        """, (user_id, transaction_type, amount, balance_after,
              is_fraud, fraud_score))

        conn.commit()
        conn.close()

    def get_user_transactions(self, user_id, limit=10):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM transactions
        WHERE user_id=?
        ORDER BY timestamp DESC
        LIMIT ?
        """, (user_id, limit))

        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return transactions

    def get_transaction_stats(self, user_id, days=30):
        """Statistics used for fraud detection"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """SELECT COUNT(*) as count FROM transactions
               WHERE user_id=? AND date(timestamp)=date('now')""",
            (user_id,)
        )
        transactions_today = cursor.fetchone()["count"]

        cursor.execute(
            """SELECT AVG(amount) as avg_amount FROM transactions
               WHERE user_id=? AND timestamp >= datetime('now','-30 days')""",
            (user_id,)
        )

        avg_amount = cursor.fetchone()["avg_amount"] or 0

        cursor.execute(
            """SELECT MAX(timestamp) as last_time FROM transactions
               WHERE user_id=?""",
            (user_id,)
        )

        last_time = cursor.fetchone()["last_time"]

        if last_time:
            last_dt = datetime.fromisoformat(last_time)
            hours = (datetime.now() - last_dt).total_seconds() / 3600
        else:
            hours = 24

        cursor.execute(
            """SELECT COUNT(DISTINCT location) as count FROM transactions
               WHERE user_id=? AND timestamp >= datetime('now','-7 days')""",
            (user_id,)
        )

        unique_locations = cursor.fetchone()["count"]

        conn.close()

        return {
            "transactions_today": transactions_today,
            "avg_amount_30days": avg_amount,
            "time_since_last_transaction": hours,
            "unique_locations_week": unique_locations if unique_locations > 0 else 1
        }

    def get_all_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users")
        users = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return users

    def block_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET is_blocked=1 WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()

    def unblock_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET is_blocked=0 WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()


if __name__ == "__main__":
    print("🗄️ Initializing database...")
    db = Database()

    print("\n📋 Sample Users")
    print("Account: 1234567890 PIN:1234")
    print("Account: 0987654321 PIN:5678")
    print("Account: 1111222233 PIN:9999")
    print("Account: 4444555566 PIN:0000")

    print("\n🔑 Admin Login")
    print("Username: admin")
    print("Password: admin123")