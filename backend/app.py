import base64
import io
import os
import sqlite3

import qrcode
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Allow CORS for frontend requests
CORS(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'server_data.db')

# Initialize database if not exists
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                description TEXT NOT NULL,
                link TEXT NOT NULL,
                qr_base64 TEXT NOT NULL
            )
        ''')
        conn.commit()
init_db()

# Route 1: Get all data for web display
@app.route('/api/data', methods=['GET'])
def get_data():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, description, link, qr_base64 FROM entries ORDER BY id DESC")
        rows = cursor.fetchall()
        # Convert rows to dictionary for JSON response
        data = [
            {
                "username": r[0],
                "description": r[1],
                "link": r[2],
                "qr_base64": r[3]
            } for r in rows
        ]
    return jsonify(data)


# Route 2: receive data, generate QR Code, and save to SQLite
@app.route('/api/submit', methods=['POST'])
def submit_data():
    req_data = request.json
    username = req_data.get('username')
    description = req_data.get('description')
    link = req_data.get('link')

    if not all([username, description, link]):
        return jsonify({"error": "Missing data! กรอกให้ครบทุกช่อง"}), 400

    # 2.1 Generate QR Code from link
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # 2.2 Convert QR Code to string (Base64) for web display
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    qr_data_uri = f"data:image/png;base64,{qr_base64}"

    # 2.3 save to SQLite
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO entries (username, description, link, qr_base64) VALUES (?, ?, ?, ?)",
            (username, description, link, qr_data_uri)
        )
        conn.commit()
    return jsonify({"message": "Saved successfully!", "qr_code": qr_data_uri}), 201


# Route 3: Clear All Data
@app.route('/api/clear', methods=['DELETE'])
def clear_data():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entries")
        conn.commit()
    return jsonify({"message": "All data cleared!"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000'))
    app.run(host='0.0.0.0', port=port, debug=True)
