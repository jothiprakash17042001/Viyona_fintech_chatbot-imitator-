import json
import sqlite3
import datetime
from flask import Flask, request, jsonify, render_template
from typing import Dict, Any, Optional, TypedDict

class LeadData(TypedDict, total=False):
    name: str
    phone: str
    email: str
    question: str

class UserState(TypedDict):
    node_id: str
    data: LeadData

app = Flask(__name__)

# Load chatbot flow
with open("flow.json", "r", encoding="utf-8") as f:
    data = json.load(f)

questions = data["intents"]["payload"]["questions"]
nodes = {node["id"]: node for node in questions}
start_node_id = "c9c43ba6-91b1-4f35-afae-202ebbb04bd7"

# Explicitly type the user_states to satisfy the linter
user_states: Dict[str, UserState] = {}

def init_db():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT,
            question TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def save_lead(lead_data: Dict[str, Any]):
    try:
        conn = sqlite3.connect("leads.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leads (name, phone, email, question)
            VALUES (?, ?, ?, ?)
        ''', (lead_data.get("name"), lead_data.get("phone"), lead_data.get("email"), lead_data.get("question")))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving lead: {e}")
        return False

def get_next_node_id(node: Dict[str, Any], user_input: str) -> Optional[str]:
    normalized = user_input.strip().lower()

    # Allow the user to go back to the start at any time
    if normalized in {"back", "main menu", "start over"}:
        return start_node_id

    if node.get("type") == "button":
        for option in node.get("options", []):
            if normalized == option["value"].strip().lower():
                return option["next"]["target"]
    elif node.get("type") == "email":
        return "__EMAIL_SUBMITTED__"
    elif node.get("next") and node["next"].get("target"):
        return node["next"]["target"]
    return None

def get_options(node: Dict[str, Any]):
    if node.get("type") == "button":
        return [opt["value"] for opt in node.get("options", [])]
    return []

def get_links(node: Dict[str, Any]):
    if node.get("links"):
        return node["links"]
    return []

def get_combined_node_data(node_id: str):
    node = nodes.get(node_id)
    if not node:
        return None, None, [], [], node_id
    
    label1 = node.get("label", "")
    label2 = None
    options = get_options(node)
    links = get_links(node)
    final_node_id = node_id
    
    # Auto-forward if it's a statement/contact with no options and has a next target
    if not options and node.get("type") in {"statement", "contact"}:
        target = node.get("next", {}).get("target")
        if target and target in nodes:
            next_node = nodes[target]
            label2 = next_node.get("label", "")
            options = get_options(next_node)
            links = get_links(next_node)
            final_node_id = target
            
    return label1, label2, options, links, final_node_id

@app.route("/chat", methods=["POST"])
def chat():
    user_id = request.remote_addr
    # request.json can be None, handled safely
    json_data = request.json or {}
    user_input = str(json_data.get("message", "")).strip()

    if user_input == "":
        label1, label2, options, links, final_id = get_combined_node_data(start_node_id)
        if not label1:
            return jsonify({"bot": "Welcome to Viyona Fintech.", "options": ["Start"]})
            
        user_states[user_id] = UserState(node_id=final_id, data=LeadData())
        return jsonify({
            "bot": label1,
            "second_line": label2,
            "options": options,
            "links": links
        })

    state = user_states.get(user_id)
    if not isinstance(state, dict):
        state = UserState(node_id=start_node_id, data=LeadData())
        user_states[user_id] = state

    current_node_id = state.get("node_id", start_node_id)
    node = nodes.get(current_node_id)
    
    if not node:
        node = nodes.get(start_node_id)
        if not node:
            return jsonify({"bot": "Session timeout. Please refresh.", "options": []})

    # Store data if current node is a collection node
    node_type = node.get("type")
    if node_type in {"name", "phone", "email", "question"}:
        data_dict = state.get("data")
        if not isinstance(data_dict, dict):
            data_dict = {}
            state["data"] = data_dict
        data_dict[node_type] = user_input

    next_id = get_next_node_id(node, user_input)

    # Fallback to sequence if target missing
    if not next_id or next_id not in nodes:
        node_list = list(nodes.keys())
        try:
            curr_idx = node_list.index(current_node_id)
            if curr_idx + 1 < len(node_list):
                next_id = node_list[curr_idx + 1]
        except (ValueError, IndexError):
            pass

    if next_id and next_id in nodes:
        label1, label2, options, links, final_id = get_combined_node_data(next_id)
        
        # Ensure data is passed along correctly
        final_data = state.get("data", LeadData())
        user_states[user_id] = UserState(node_id=final_id, data=final_data)
        
        # Save lead if final node
        next_node = nodes[final_id]
        label_text = str(next_node.get("label", "")).lower()
        if "thank you" in label_text:
            save_lead(final_data)
            user_states[user_id] = UserState(node_id=start_node_id, data=LeadData())

        # Hide navigation buttons during lead collection steps to keep the space clean
        if final_id != start_node_id and next_node.get("type") not in {"name", "phone", "email", "question"}:
            if "Back" not in options: options.append("Back")
            if "Main Menu" not in options: options.append("Main Menu")

        return jsonify({
            "bot": label1,
            "second_line": label2,
            "options": options,
            "links": links
        })

    return jsonify({
        "bot": "Please select an option or use the Main Menu.",
        "options": get_options(node) + ["Main Menu"],
        "links": get_links(node)
    })

@app.route("/")
def serve_chat():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)