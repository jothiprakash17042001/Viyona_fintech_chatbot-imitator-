import json
from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

# Load the chatbot flow
with open("flow.json", "r", encoding="utf-8") as f:
    data = json.load(f)

questions = data["intents"]["payload"]["questions"]
nodes = {node["id"]: node for node in questions}
start_node_id = "c9c43ba6-91b1-4f35-afae-202ebbb04bd7"

user_states = {}

def get_next_node_id(node, user_input):
    if node.get("type") == "button":
        for option in node.get("options", []):
            if user_input.strip().lower() == option["value"].strip().lower():
                return option["next"]["target"]
    # Allow free text for name, email, phone, question, etc.
    elif node.get("type") == "email":
        # After email, show 'submitted' message instead of next node
        return "__EMAIL_SUBMITTED__"
    elif node.get("type") in ["name", "phone", "question"] and node.get("next") and node["next"].get("target"):
        return node["next"]["target"]
    elif node.get("next") and node["next"].get("target"):
        return node["next"]["target"]
    return None

def get_options(node):
    if node.get("type") == "button":
        return [opt["value"] for opt in node.get("options", [])]
    return []

@app.route("/chat", methods=["POST"])
def chat():
    user_id = request.remote_addr
    user_input = request.json.get("message", "")
    current_node_id = user_states.get(user_id, start_node_id)
    node = nodes.get(current_node_id)

    # Always reset to start node if user_input is empty (on refresh or first load)
    if not user_input.strip():
        node = nodes.get(start_node_id)
        bot_message = node.get("label", "")
        options = get_options(node)
        user_states[user_id] = start_node_id
        return jsonify({"bot": bot_message, "options": options})

    next_id = get_next_node_id(node, user_input)
    if next_id == "__EMAIL_SUBMITTED__":
        user_states[user_id] = start_node_id  # Optionally reset or keep at current
        return jsonify({"bot": "Submitted", "options": []})
    elif next_id:
        next_node = nodes.get(next_id)
        bot_message = next_node.get("label", "")
        options = get_options(next_node)
        user_states[user_id] = next_id
        return jsonify({"bot": bot_message, "options": options})
    else:
        return jsonify({"bot": "Sorry, I didn't understand that.", "options": get_options(node)})

@app.route("/")
def serve_chat():
    return render_template("chat.html")

if __name__ == "__main__":
    app.run(debug=True)