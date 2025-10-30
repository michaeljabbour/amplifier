Comprehensive Application Terminal-Bench Task
We will create a new Terminal-Bench task called contact-manager-api. This task challenges an AI agent to build a comprehensive web application (a contact management REST API) from scratch, including setting up an HTTP server and a persistent database. It is designed to test complex multi-step reasoning and coding skills – suitable for advanced models like GPT-5 or Claude Opus – while still being solvable with proper planning. The task files are structured according to Terminal-Bench guidelines[1], including a Dockerfile for the environment, a YAML description, a reference solution, and an automated test script.
Model Variants and Use Cases
This benchmark task is intended to be run with multiple model variants to compare their performance. Below we outline the targeted model variants and their ideal use cases:
GPT-5 – Best for complex reasoning, broad world knowledge, and code-heavy multi-step tasks.
GPT-5-mini – A cost-optimized version balancing speed and capability; suitable for medium-complexity reasoning and general chat interactions.
GPT-5-nano – A high-throughput, lightweight model for simple instruction-following or classification tasks (may struggle with this task’s complexity).
Claude-Opus-4-1 – Anthropic Claude variant analogous to GPT-5, excelling at extensive reasoning and intricate coding tasks.
Claude-Sonnet-4-5 – A mid-tier Claude model balancing performance and cost, capable of moderate reasoning and coding with some efficiency.
Claude-Haiku-4-5 – A smaller Claude model optimized for speed; suitable for straightforward tasks or quick responses (likely insufficient for full task completion here).
By running the contact-manager-api task across these variants, we can observe how the larger models handle the full application requirements versus how the smaller, cost-effective models perform.
Task Files
Below are the complete files for the contact-manager-api task. This includes the environment setup, task description (with requirements and success criteria), an example solution script, and the test code that verifies task completion. All code and configuration is provided in full.
tasks/contact-manager-api/Dockerfile
This Dockerfile defines the sandbox environment for the task. We use a slim Python base image, install Flask (for the web server), Requests (for HTTP calls in tests), and Pytest (for running the validation script). We also set the working directory to /app (the default location for task files in Terminal-Bench containers) and ensure all necessary packages are installed for the agent and tests.
FROM python:3.10-slim

# Set working directory for the task
WORKDIR /app

# Install required Python packages for server and testing
RUN pip install flask requests pytest
tasks/contact-manager-api/task.yaml
The YAML configuration file defines the task metadata and the instructions given to the agent. It includes a clear description of what the agent must accomplish, along with metadata like difficulty, tags, author contact, and execution timeouts. The instructions specify that the agent needs to create a web server with specific endpoints and use a SQLite database for persistence. We explicitly instruct the agent to run the server in the background so that it remains active during testing (as seen in similar tasks like the Jupyter server setup[2]). The success criteria indicate what the automated test will verify.
description: |
  You are a software engineer tasked with creating a small **contact management web API** application from scratch. The goal is to implement and launch a web server that can **store and retrieve contact information**. Follow these requirements to complete the task:

  1. **Web Server**: Set up an HTTP server (for example, using a Python web framework or any suitable tool) listening on **port 5000** and accepting connections from any IP (host `0.0.0.0`).
  2. **Create Contact Endpoint (POST)**: Implement a **POST** endpoint at `/contacts` that accepts a JSON payload with at least `"name"` and `"phone"` fields. On success, this endpoint should **store the contact** in a persistent database and return a JSON response containing the saved contact's details **including a unique ID**.
  3. **List Contacts Endpoint (GET)**: Implement a **GET** endpoint at `/contacts` that returns a JSON **list of all contacts** currently stored. Each contact object in the list should include its `"id"`, `"name"`, and `"phone"`.
  4. **Data Persistence**: Use a SQLite database (or a similar file-based database) to store contacts so that multiple requests can access shared data. The database file (e.g. `contacts.db`) should be created in the working directory (*/app/*).
  5. **Background Server**: Launch or fork the server process in the **background** (e.g., using `&` or a similar mechanism) and leave it running so that it continues to serve requests while the task is being evaluated. **Do not terminate the server** before finishing the task – it must remain active for test queries.

  *Notes*: You may use any programming language or framework available in the environment to implement the server and database. Ensure that the server is running on the correct port and that the API endpoints meet the specifications above.

  **Success criteria**: The automated test will perform the following checks to verify your solution:
  - **POST /contacts**: The test will send a sample contact (with a name and phone number). The API must respond with a **200 OK or 201 Created** status and return a JSON object containing the saved contact (including a generated `id`, and matching name and phone).
  - **GET /contacts**: After adding a contact, the test will send a GET request to `/contacts`. The API should respond with **200 OK** and return a JSON list that includes the previously added contact. The contact’s details in the list must match what was provided (same `name` and `phone`, and the correct `id`).

difficulty: medium
category: software-engineering
tags: [web, database, api]
author_email: michael.jabbour@gmail.com
max_agent_timeout_sec: 300
max_test_timeout_sec: 30
tasks/contact-manager-api/solution.sh
The reference solution script provides one way to solve the task (this is how an ideal agent – the Oracle – would complete it). The solution installs Flask (in case it isn’t already installed), writes a Python server program (server.py) that implements the required API using Flask and SQLite, and then starts the server in the background. We use nohup and an ampersand (&) to ensure the server keeps running after the script ends, and we include a short sleep to give the server time to start up. By the end of this script, the Flask server is listening on port 5000 and ready to handle requests, fulfilling all task requirements.
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
tasks/contact-manager-api/tests/test_outputs.py
The test script uses the Requests library to verify that the API works as expected. It first posts a sample contact ("Alice", with phone number "123456") to the /contacts endpoint, then checks the HTTP response status and JSON content. It asserts that the response contains an id and that the returned name and phone match the input. Next, it sends a GET request to /contacts and checks that the response is a list containing the newly added contact (by matching the id and fields). If any of these conditions fail, the test will raise an assertion error, causing the task to be marked as unsuccessful. If all assertions pass, the task is considered solved.
import requests
import time

def test_contact_manager_api():
    # Give the server a brief moment to ensure it's running (if needed)
    time.sleep(1)

    # 1. Test adding a new contact via POST
    new_contact = {"name": "Alice", "phone": "123456"}
    resp = requests.post("http://localhost:5000/contacts", json=new_contact)
    assert resp.status_code in (200, 201), f"POST /contacts returned {resp.status_code}, expected 200 or 201."
    data = resp.json()
    # Verify the returned JSON contains the correct data and an id
    assert data.get("name") == "Alice" and data.get("phone") == "123456", "POST /contacts response JSON data mismatch."
    assert "id" in data, "POST /contacts response missing 'id' field."
    contact_id = data["id"]

    # 2. Test retrieving contacts via GET
    resp2 = requests.get("http://localhost:5000/contacts")
    assert resp2.status_code == 200, f"GET /contacts returned {resp2.status_code}, expected 200."
    contacts_list = resp2.json()
    assert isinstance(contacts_list, list), "GET /contacts did not return a JSON list."
    # There should be at least one contact and the one we added should be present
    matching_contacts = [c for c in contacts_list if c.get("id") == contact_id]
    assert matching_contacts, "Added contact not found in GET /contacts list."
    found = matching_contacts[0]
    assert found.get("name") == "Alice" and found.get("phone") == "123456", "Contact data in list does not match expected values."
Each of the above files works together to define the contact-manager-api task. An agent evaluated on this task must read the instructions, install and utilize appropriate tools or libraries, write and execute code to start the web server, and leave the server running. The test will then interact with the agent’s application to verify correct functionality. This comprehensive task setup will allow us to assess the capabilities of different model variants (GPT-5 family and Claude family) in handling end-to-end software development tasks within a terminal environment. The larger models should excel at the complex, multi-step requirements, while the smaller variants might struggle with the breadth of actions needed, illustrating the trade-offs between model size and task competence.
[1] Quickstart
https://www.tbench.ai/docs/task-quickstart
[2] Terminal-Bench
https://www.tbench.ai/registry/terminal-bench-core/0.1.1
