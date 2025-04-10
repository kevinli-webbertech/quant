from flask import Flask, render_template, request, redirect
from symbol_db import (
    create_tables,
    add_tag,
    add_symbol,
    link_symbol_to_tags,
    search_symbols_by_tag
)

app = Flask(__name__)

# Create tables at app startup
create_tables()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handle form submission to add a new symbol
        category = request.form["category"]
        title = request.form["title"]
        body = request.form["body"]
        comment = request.form["comment"]
        due_date = request.form["due_date"]
        priority = request.form["priority"]
        tags_input = request.form["tags"]

        # Save the new symbol entry
        symbol_id = add_symbol(category, title, body, comment, due_date, priority)

        # Process tags
        tag_list = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        for tag in tag_list:
            add_tag(tag)
        link_symbol_to_tags(symbol_id, tag_list)

        # Redirect to home page after successful add
        return redirect("/")

    # Initial GET request (show empty form)
    return render_template("index.html", results=None)

@app.route("/search", methods=["GET"])
def search():
    tag = request.args.get("tag", "").strip()
    results = search_symbols_by_tag(tag) if tag else []
    return render_template("index.html", results=results, tag=tag)

if __name__ == "__main__":
    app.run(debug=True)
