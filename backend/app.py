import os
import re
import mysql.connector
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# Constants
ERR_DATABASE = "Database error"

# Security Fix: Dynamic Environment-Driven CORS
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
origins_list = [origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()]

CORS(app, resources={r"/api/*": {"origins": origins_list}})

# -------------------------
# Helper Functions & Validation
# -------------------------
def is_valid_indian_phone(phone: str) -> bool:
    """Validate 10-digit Indian phone numbers starting with 6, 7, 8, or 9"""
    if not phone or not isinstance(phone, str):
        return False
    return bool(re.match(r"^[6-9]\d{9}$", phone))

# -------------------------
# Menu Data
# -------------------------
menu = [
    {"name": "Masala Tea", "price": 20, "category": "tea", "emoji": "☕", "description": "Fresh Indian Masala Tea"},
    {"name": "Ginger Tea", "price": 20, "category": "tea", "emoji": "🫖", "description": "Hot Adrak Chai"},
    {"name": "Veg Momos", "price": 40, "category": "Momos", "emoji": "🥟", "description": "Steamed / Fried"},
    {"name": "Paneer Momos", "price": 80, "category": "Momos", "emoji": "🧀", "description": "Cheesy Paneer Filling"},
    {"name": "Veg Burger", "price": 60, "category": "snacks", "emoji": "🍔", "description": "Fresh Veg Patty Burger"},
    {"name": "Cheese Maggi", "price": 50, "category": "snacks", "emoji": "🍜", "description": "Loaded with Cheese"},
    {"name": "White Sauce Pasta", "price": 90, "category": "chinese", "emoji": "🍝", "description": "Creamy Italian Style"},
    {"name": "Grilled Sandwich", "price": 70, "category": "snacks", "emoji": "🥪", "description": "Loaded Veg Sandwich"},
    {"name": "Veg Fried Rice", "price": 90, "category": "chinese", "emoji": "🍚", "description": "Chinese Style Rice"},
    {"name": "Veg Chowmein", "price": 80, "category": "chinese", "emoji": "🥡", "description": "Street Style Noodles"},
    {"name": "Chicken Chowmein", "price": 100, "category": "chinese", "emoji": "🥡", "description": "Chicken Noodles"}
]

# -------------------------
# Database Connection Helper
# -------------------------
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'mysql-service'),
        user=os.environ.get('DB_USER', 'chai_admin'),
        password=os.environ.get('DB_PASSWORD', 'UserPassword123'),
        database=os.environ.get('DB_NAME', 'chaipolitics_db'),
        connect_timeout=5
    )

# -------------------------
# Auto-Initialize Database Schema
# -------------------------
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(15) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Cart table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                user_name VARCHAR(100),
                user_phone VARCHAR(15),
                item_name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                quantity INT DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_phone) REFERENCES users(phone) ON DELETE CASCADE
            );
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("Database schema initialized successfully.", flush=True)
    except Exception as e:
        print(f"Schema Initialization Warning (will retry on query execution): {str(e)}", flush=True)

# Safe schema initialization attempt on backend load
init_db()

# -------------------------
# Health & General APIs
# -------------------------
@app.route("/")
@app.route("/health")
def health():
    """Endpoint used by GKE Ingress and Kubernetes Readiness/Liveness Probes"""
    return jsonify({"status": "healthy", "service": "chai-politics-backend"}), 200

@app.route("/api/menu")
def get_menu():
    return jsonify(menu), 200

@app.route("/api/version")
def version():
    return jsonify({
        "application": "Chai Politics",
        "version": "1.0.0",
        "environment": "Production"
    }), 200

# -------------------------
# User Authentication APIs
# -------------------------

# 1. Existing User Login Route
@app.route("/api/login", methods=["POST"])
def login_user():
    data = request.get_json(silent=True) or {}
    phone = data.get("phone", "").strip()

    if not phone or not is_valid_indian_phone(phone):
        return jsonify({"error": "A valid 10-digit phone number is required!"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, name, phone FROM users WHERE phone = %s", (phone,))
        user = cursor.fetchone()
        cursor.close()

        if not user:
            return jsonify({"error": "Account not found. Please register first."}), 404

        return jsonify({
            "message": "Login successful!",
            "user_id": user["id"],
            "name": user["name"],
            "phone": user["phone"]
        }), 200

    except Exception as e:
        print(f"Login Error: {str(e)}", flush=True)
        return jsonify({"error": ERR_DATABASE, "details": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


# 2. New User Registration Route
@app.route("/api/register", methods=["POST"])
def register_user():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()

    if not name:
        return jsonify({"error": "Name is required!"}), 400

    if not phone or not is_valid_indian_phone(phone):
        return jsonify({"error": "A valid 10-digit phone number is required!"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id FROM users WHERE phone = %s", (phone,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            return jsonify({"error": "Phone number already registered. Please login."}), 409

        cursor.execute("INSERT INTO users (name, phone) VALUES (%s, %s)", (name, phone))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()

        return jsonify({
            "message": "Registration successful!",
            "user_id": user_id,
            "name": name,
            "phone": phone
        }), 201

    except Exception as e:
        print(f"Register Error: {str(e)}", flush=True)
        return jsonify({"error": ERR_DATABASE, "details": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

# -------------------------
# Cart Operations APIs
# -------------------------

# 1. Add Item to Cart
@app.route("/api/cart", methods=["POST"])
def add_to_cart():
    data = request.get_json(silent=True) or {}
    user_phone = data.get("user_phone", "").strip()
    item_name = data.get("item_name", "").strip()
    price = data.get("price")
    quantity = data.get("quantity", 1)

    if not user_phone or not is_valid_indian_phone(user_phone) or not item_name or price is None:
        return jsonify({"error": "Valid user_phone, item_name, and price are required!"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, name FROM users WHERE phone = %s", (user_phone,))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            return jsonify({"error": "User not registered!"}), 401

        query = """
            INSERT INTO cart (user_id, user_name, user_phone, item_name, price, quantity)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user["id"], user["name"], user_phone, item_name, price, quantity))
        conn.commit()
        cursor.close()

        return jsonify({"message": f"Added {item_name} to cart!"}), 201

    except Exception as e:
        print(f"Add Cart Error: {str(e)}", flush=True)
        return jsonify({"error": ERR_DATABASE, "details": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


# 2. Get Cart Items by Phone
@app.route("/api/cart/<string:phone>", methods=["GET"])
def get_cart_by_phone(phone):
    if not is_valid_indian_phone(phone):
        return jsonify({"error": "Invalid phone number requested"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM cart WHERE user_phone = %s ORDER BY created_at DESC"
        cursor.execute(query, (phone,))
        cart_items = cursor.fetchall()
        cursor.close()

        return jsonify(cart_items), 200

    except Exception as e:
        print(f"Get Cart Error: {str(e)}", flush=True)
        return jsonify({"error": ERR_DATABASE, "details": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


# 3. Clear Cart / Place Order (Delete items by Phone)
@app.route("/api/cart/<string:phone>", methods=["DELETE"])
def clear_cart(phone):
    if not is_valid_indian_phone(phone):
        return jsonify({"error": "Invalid phone number requested"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM cart WHERE user_phone = %s", (phone,))
        conn.commit()
        cursor.close()

        return jsonify({"message": "Cart cleared successfully!"}), 200

    except Exception as e:
        print(f"Clear Cart Error: {str(e)}", flush=True)
        return jsonify({"error": ERR_DATABASE, "details": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    # Docker/K8s ke liye default host 0.0.0.0 par bind karo
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1']
    
    app.run(host=host, port=port, debug=debug)