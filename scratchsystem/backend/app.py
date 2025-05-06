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
        symbol_id = add_symbol(
            data["category"], data["title"], data["body"], data["comment"],
            data["due_date"], data["priority"]
        )
        for tag in data.get("tags", []):
            add_tag(tag)
        link_symbol_to_tags(symbol_id, data.get("tags", []))
        return jsonify({"id": symbol_id}), 201
    except Exception as e:
        print("❌ Error in POST /symbols:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/symbols/search")
def search():
    try:
        tag = request.args.get("tag", "").strip()
        raw_results = search_symbols_by_tag(tag) if tag else []
        results = [
            {
                "id": row[0],
                "title": row[1] or "",
                "category": row[2] or "code",
                "body": row[3] or "",
                "comment": row[4] or "",
                "due_date": row[5] or "",
                "priority": row[6] or "medium",
            } for row in raw_results
        ]
        return jsonify(results)
    except Exception as e:
        print("❌ Error in /symbols/search:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/symbols/<int:symbol_id>", methods=["GET"])
def get_symbol(symbol_id):
    try:
        result = get_symbol_by_id(symbol_id)
        if "error" in result:
            return jsonify(result), 404
        return jsonify(result)
    except Exception as e:
        print("🔥 ERROR in GET /symbols/<id>:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/symbols/<int:symbol_id>", methods=["PUT"])
def update(symbol_id):
    try:
        data = request.get_json()
        update_symbol(
            symbol_id,
            data["category"],
            data["title"],
            data["body"],
            data["comment"],
            data["due_date"],
            data["priority"]
        )

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM symbol_tag WHERE symbol_id = ?", (symbol_id,))
        conn.commit()
        conn.close()

        for tag in data.get("tags", []):
            add_tag(tag)
        link_symbol_to_tags(symbol_id, data.get("tags", []))

        return jsonify({"status": "updated"}), 200
    except Exception as e:
        print("🔥 Error in PUT /symbols/<id>:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/symbols/<int:symbol_id>", methods=["DELETE"])
def delete(symbol_id):
    try:
        delete_symbol(symbol_id)
        return jsonify({"status": "deleted"}), 200
    except Exception as e:
        print("🔥 Error in DELETE /symbols/<id>:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
