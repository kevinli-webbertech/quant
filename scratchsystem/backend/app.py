from flask import Flask, request, jsonify
from flask_cors import CORS
from symbol_db import *

app = Flask(__name__)
CORS(app)
create_tables()

@app.route("/symbols", methods=["POST"])
def create_symbol():
    try:
        data = request.get_json()
        print("Received data:", data)
        symbol_id = add_symbol(
            data["category"], data["title"], data["body"], data["comment"],
            data["due_date"], data["priority"]
        )
        for tag in data.get("tags", []):
            add_tag(tag)
        link_symbol_to_tags(symbol_id, data.get("tags", []))
        return jsonify({"id": symbol_id}), 201
    except Exception as e:
        print("Error in /symbols:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/symbols/search")
def search():
    try:
        tag = request.args.get("tag", "").strip()
        raw_results = search_symbols_by_tag(tag) if tag else []
        results = [
            {
                "id": row[0],
                "title": row[1],
                "category": row[2],
                "priority": row[3],
                "body": row[4]
            } for row in raw_results
        ]
        return jsonify(results)
    except Exception as e:
        print("Error in /symbols/search:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/symbols/<int:symbol_id>", methods=["GET"])
def get_symbol(symbol_id):
    symbol = get_symbol_by_id(symbol_id)
    return jsonify(symbol)

@app.route("/symbols/<int:symbol_id>", methods=["PUT"])
@app.route("/symbols/<int:symbol_id>", methods=["PUT"])
@app.route("/symbols/<int:symbol_id>", methods=["PUT"])
def update(symbol_id):
    try:
        data = request.get_json()
        print(f"\nReceived UPDATE for ID {symbol_id}:")
        print("Payload:", data)

        update_symbol(
            symbol_id,
            data["category"],
            data["title"],
            data["body"],
            data["comment"],
            data["due_date"],
            data["priority"]
        )

        # Remove old tags
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM symbol_tag WHERE symbol_id = ?", (symbol_id,))
        conn.commit()
        conn.close()

        print("Old tags removed.")

        # Re-link new tags (if any)
        for tag in data.get("tags", []):
            add_tag(tag)
        link_symbol_to_tags(symbol_id, data.get("tags", []))

        print("New tags linked.")
        return jsonify({"status": "updated"}), 200
    except Exception as e:
        print("❌ Error in PUT /symbols/<id>:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/symbols/<int:symbol_id>", methods=["DELETE"])
def delete(symbol_id):
    try:
        delete_symbol(symbol_id)
        return jsonify({"status": "deleted"}), 200
    except Exception as e:
        print("Error in DELETE /symbols/<id>:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
