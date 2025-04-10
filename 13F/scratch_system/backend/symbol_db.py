import sqlite3
from datetime import datetime

DB_NAME = "symbol_tracker.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tag (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tag_name TEXT NOT NULL UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS symbol (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL CHECK(category IN ('symbol', 'event', 'code', 'kb')),
        title TEXT NOT NULL,
        body TEXT,
        comment TEXT,
        created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        due_date TIMESTAMP,
        priority TEXT CHECK(priority IN ('low', 'medium', 'high'))
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS symbol_tag (
        symbol_id INTEGER,
        tag_id INTEGER,
        PRIMARY KEY (symbol_id, tag_id),
        FOREIGN KEY (symbol_id) REFERENCES symbol(id),
        FOREIGN KEY (tag_id) REFERENCES tag(id)
    )
    ''')

    conn.commit()
    conn.close()


def add_tag(tag_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tag (tag_name) VALUES (?)", (tag_name,))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Tag '{tag_name}' already exists.")
    conn.close()


def add_symbol(category, title, body, comment, due_date, priority):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO symbol (category, title, body, comment, due_date, priority)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (category, title, body, comment, due_date, priority))
    conn.commit()
    symbol_id = cursor.lastrowid
    conn.close()
    return symbol_id


def link_symbol_to_tags(symbol_id, tag_names):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for tag_name in tag_names:
        cursor.execute("SELECT id FROM tag WHERE tag_name = ?", (tag_name,))
        tag = cursor.fetchone()
        if tag:
            tag_id = tag[0]
            try:
                cursor.execute("INSERT INTO symbol_tag (symbol_id, tag_id) VALUES (?, ?)", (symbol_id, tag_id))
            except sqlite3.IntegrityError:
                pass  # Already linked
        else:
            print(f"Tag '{tag_name}' does not exist.")
    conn.commit()
    conn.close()


def search_symbols_by_tag(tag_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.id, s.title, s.category, s.priority, s.body
        FROM symbol s
        JOIN symbol_tag st ON s.id = st.symbol_id
        JOIN tag t ON st.tag_id = t.id
        WHERE t.tag_name = ?
    ''', (tag_name,))
    results = cursor.fetchall()
    conn.close()
    return results


# ---------- Example Usage ----------

if __name__ == "__main__":
    create_tables()

    # Add tags
    add_tag("java")
    add_tag("binary tree")

    # Add a symbol
    symbol_id = add_symbol(
        category="code",
        title="Java Binary Search Tree Insert",
        body="public class TreeNode {...}",  # Replace with real code
        comment="Leetcode question reference",
        due_date="2025-05-01 00:00:00",
        priority="medium"
    )

    # Link symbol to tags
    link_symbol_to_tags(symbol_id, ["java", "binary tree"])

    # Search by tag
    matches = search_symbols_by_tag("java")
    for row in matches:
        print("ID:", row[0], "| Title:", row[1], "| Category:", row[2], "| Priority:", row[3])
        print("Body:", row[4][:100] + "...\n")
