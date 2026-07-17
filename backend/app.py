from flask import Flask, jsonify

app = Flask(__name__)

# -------------------------
# Menu Data
# -------------------------

menu = [
    {"name": "Masala Tea", "price": 15},
    {"name": "Ginger Tea", "price": 20},
    {"name": "Veg Momos", "price": 40},
    {"name": "Paneer Momos", "price": 60},
    {"name": "Veg Burger", "price": 60},
    {"name": "Cheese Maggi", "price": 50},
    {"name": "White Sauce Pasta", "price": 90},
    {"name": "Grilled Sandwich", "price": 70},
    {"name": "Veg Fried Rice", "price": 90},
    {"name": "Veg Chowmein", "price": 80}
]

# -------------------------
# Health Check API
# -------------------------

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