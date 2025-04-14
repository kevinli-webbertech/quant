from flask import Flask, render_template, request, redirect
from symbol_db import (
    create_tables, add_tag, add_symbol, link_symbol_to_tags,
    search_symbols_by_tag, get_symbol_by_id, delete_symbol, update_symbol
)


app = Flask(__name__)
create_tables()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        category = request.form["category"]
        title = request.form["title"]
        body = request.form["body"]
        comment = request.form["comment"]
        due_date = request.form["due_date"]
        priority = request.form["priority"]
        tags_input = request.form["tags"]
        tag_list = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

        symbol_id = add_symbol(category, title, body, comment, due_date, priority)
        for tag in tag_list:
            add_tag(tag)
        link_symbol_to_tags(symbol_id, tag_list)

        return redirect("/")

    return render_template("index.html", results=None)

@app.route("/search", methods=["GET"])
def search():
    tag = request.args.get("tag", "").strip()
    results = search_symbols_by_tag(tag) if tag else []
    return render_template("index.html", results=results, tag=tag)

@app.route("/delete/<int:symbol_id>", methods=["POST"])
def delete(symbol_id):
    delete_symbol(symbol_id)
    return redirect("/")

@app.route("/edit/<int:symbol_id>", methods=["GET", "POST"])
def edit(symbol_id):
    if request.method == "POST":
        category = request.form["category"]
        title = request.form["title"]
        body = request.form["body"]
        comment = request.form["comment"]
        due_date = request.form["due_date"]
        priority = request.form["priority"]
        update_symbol(symbol_id, category, title, body, comment, due_date, priority)
        return redirect("/")

    symbol = get_symbol_by_id(symbol_id)
    return render_template("edit.html", symbol=symbol)

if __name__ == "__main__":
    app.run(debug=True)
