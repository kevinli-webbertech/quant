from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS

app = Flask(__name__)

# ✅ Enable CORS for React frontend
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# ✅ Connect to the Database
def get_db_connection():
    db_path = 'investment.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# ✅ Fetch all bank accounts
@app.route('/api/bank_accounts', methods=['GET'])
def get_bank_accounts():
    conn = get_db_connection()
    accounts = conn.execute("SELECT * FROM bank_account").fetchall()
    conn.close()

    if not accounts:
        return jsonify({"error": "No bank accounts found"}), 404

    return jsonify([dict(account) for account in accounts])

# ✅ Add a new bank account
@app.route('/api/bank_accounts', methods=['POST'])
def add_bank_account():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bank_account (bank_name, account_name, account_number, routing_number, deposit_amount, current_amount, maturity_date, current_rate, comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (data.get('bank_name'), data.get('account_name'), data.get('account_number'), data.get('routing_number'),
         data.get('deposit_amount'), data.get('current_amount'), data.get('maturity_date'), data.get('current_rate'),
         data.get('comments'))
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Bank account added successfully"}), 201

# ✅ Delete a bank account
@app.route('/api/bank_accounts/<int:id>', methods=['DELETE'])
def delete_bank_account(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bank_account WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Bank account deleted successfully"}), 200

# ✅ Fetch all bonds
@app.route('/api/bonds', methods=['GET'])
def get_bonds():
    conn = get_db_connection()
    bonds = conn.execute("SELECT * FROM bond").fetchall()
    conn.close()

    if not bonds:
        return jsonify({"error": "No bonds found"}), 404

    return jsonify([dict(bond) for bond in bonds])

# ✅ Add a new bond
@app.route('/api/bonds', methods=['POST'])
def add_bond():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bond (bond_name, bond_type, bond_term, amount, maturity_date, apy, platform, comment) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (data.get('bond_name'), data.get('bond_type', 'Unknown'), data.get('bond_term'),
         data.get('amount'), data.get('maturity_date'), data.get('apy', 0),
         data.get('platform', 'N/A'), data.get('comment', ''))
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Bond added successfully"}), 201

# ✅ Delete a bond
@app.route('/api/bonds/<int:id>', methods=['DELETE'])
def delete_bond(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bond WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Bond deleted successfully"}), 200

if __name__ == '__main__':
    print("✅ Flask API is running at http://127.0.0.1:5000/")
    app.run(debug=True, host='0.0.0.0', port=5000)
