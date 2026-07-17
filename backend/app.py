from flask import Flask, jsonify

app = Flask(__name__)

# -------------------------
# Menu Data
# -------------------------
menu = [
    {"name": "Masala Tea", "price": 15, "category": "tea", "emoji": "☕", "description": "Fresh Indian Masala Tea"},
    {"name": "Ginger Tea", "price": 20, "category": "tea", "emoji": "🫖", "description": "Hot Adrak Chai"},
    {"name": "Veg Momos", "price": 40, "category": "Momos", "emoji": "🥟", "description": "Steamed / Fried"},
    {"name": "Paneer Momos", "price": 60, "category": "Momos", "emoji": "🧀", "description": "Cheesy Paneer Filling"},
    {"name": "Veg Burger", "price": 60, "category": "snacks", "emoji": "🍔", "description": "Fresh Veg Patty Burger"},
    {"name": "Cheese Maggi", "price": 50, "category": "snacks", "emoji": "🍜", "description": "Loaded with Cheese"},
    {"name": "White Sauce Pasta", "price": 90, "category": "chinese", "emoji": "🍝", "description": "Creamy Italian Style"},
    {"name": "Grilled Sandwich", "price": 70, "category": "snacks", "emoji": "🥪", "description": "Loaded Veg Sandwich"},
    {"name": "Veg Fried Rice", "price": 90, "category": "chinese", "emoji": "🍚", "description": "Chinese Style Rice"},
    {"name": "Veg Chowmein", "price": 80, "category": "chinese", "emoji": "🥡", "description": "Street Style Noodles"}
]

# -------------------------
# Health Check API
# -------------------------

# -------------------------
# Health Check API (Handles both / and /health)
# -------------------------

@app.route("/")
@app.route("/health")
def health():
    return jsonify({
        "status": "UP"
    })
# -------------------------
# Menu API
# -------------------------

@app.route("/api/menu")
def get_menu():
    return jsonify(menu)

# -------------------------
# Version API
# -------------------------

@app.route("/api/version")
def version():
    return jsonify({
        "application": "Chai Politics",
        "version": "1.0.0",
        "environment": "Production"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)