#!/bin/bash
set -e

# Install Flask (and its dependencies) if not already present
pip install flask

# Write the server application code to server.py
cat > server.py << 'EOF'
from flask import Flask, request, jsonify
import sqlite3, os

app = Flask(__name__)
DB_PATH = "contacts.db"

# Initialize database and table
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY, name TEXT, phone TEXT)"
    )
    conn.commit()
    conn.close()

init_db()

# Endpoint to add a new contact
@app.route('/contacts', methods=['POST'])
def add_contact():
    data = request.get_json(force=True)
    if data is None or 'name' not in data or 'phone' not in data:
        return jsonify({"error": "Missing name or phone"}), 400
    name = data['name']
    phone = data['phone']
    # Insert into database
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", (name, phone))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    # Return the created contact with its new ID
    return jsonify({"id": new_id, "name": name, "phone": phone}), 201

# Endpoint to list all contacts
@app.route('/contacts', methods=['GET'])
def get_contacts():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone FROM contacts")
    rows = cur.fetchall()
    conn.close()
    contacts = []
    for (cid, cname, cphone) in rows:
        contacts.append({"id": cid, "name": cname, "phone": cphone})
    return jsonify(contacts), 200

if __name__ == '__main__':
    # Run the server on port 5000, accessible from any host (0.0.0.0)
    app.run(host='0.0.0.0', port=5000)
EOF

# Start the server in the background and ensure it stays running
nohup python3 server.py > server.log 2>&1 &

# Wait a moment to ensure the server has started
sleep 2