import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'investment.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create bank_accounts table
cursor.execute('''
CREATE TABLE IF NOT EXISTS bank_account (
    id INTEGER PRIMARY KEY,
    bank_name TEXT NOT NULL,
    account_name TEXT NOT NULL,
    account_number TEXT NOT NULL,
    routing_number TEXT,
    deposit_amount NUMERIC NULL,
    current_amount NUMERIC NOT NULL,
    maturity_date TEXT NOT NULL,
    current_rate TEXT NULL,
    comments TEXT NULL
)
''')

cursor.execute('DROP INDEX IF EXISTS bank_account_account_number_IDX')
cursor.execute('CREATE UNIQUE INDEX bank_account_account_number_IDX ON bank_account (account_number, routing_number)')

# Create bond table
cursor.execute('''
CREATE TABLE IF NOT EXISTS bond (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    bond_name TEXT,
    bond_type TEXT,
    bond_term INTEGER,
    amount INTEGER,
    maturity_date INTEGER,
    apy NUMERIC,
    platform TEXT,
    comment TEXT
)
''')

conn.commit()
conn.close()
print("Database and tables created successfully!")

