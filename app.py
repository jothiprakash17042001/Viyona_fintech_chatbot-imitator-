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
        # If user enters 'Back', and this node has Submit Details and Main Menu, show this node again
        if user_input.strip().lower() == "back":
            option_values = [opt["value"].strip().lower() for opt in node.get("options", [])]
            if "submit details" in option_values and "main menu" in option_values:
                return node["id"]  # Stay on this node to show Submit and Main Menu
            # If not, try to find a button node in the flow that has those options
            for n in nodes.values():
                if n.get("type") == "button":
                    values = [opt["value"].strip().lower() for opt in n.get("options", [])]
                    if "submit details" in values and "main menu" in values:
                        return n["id"]
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

def get_links(node):
    return node.get("links", []) if node.get("links") else []

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
        # Always show the welcome line only
        options = []
        links = []
        next_id = node.get("next", {}).get("target")
        if next_id and next_id in nodes:
            next_node = nodes[next_id]
            user_states[user_id] = next_id
            print(f"[DEBUG] Node ID: {next_id}, Links: {links}")
            # Send options of the next node as well
            return jsonify({
                "bot": bot_message,  # Only the welcome line
                "options": get_options(next_node),
                "links": [],
                "second_line": next_node.get("label", "")  # Send the second line separately
            })
        else:
            user_states[user_id] = start_node_id
            print(f"[DEBUG] Node ID: {start_node_id}, Links: {links}")
            return jsonify({"bot": bot_message, "options": options, "links": links})

    next_id = get_next_node_id(node, user_input)
    if next_id == "__EMAIL_SUBMITTED__":
        user_states[user_id] = start_node_id  # Optionally reset or keep at current
        print(f"[DEBUG] Node ID: __EMAIL_SUBMITTED__, Links: []")
        return jsonify({"bot": "“Thank you! Our team will reach out to you soon. Feel free to ask more questions or navigate options enter the back to the reach main menu”", "options": [], "links": []})
    elif next_id:
        next_node = nodes.get(next_id)
        if not next_node:
            print(f"[ERROR] Node ID {next_id} not found in flow.")
            return jsonify({"bot": "Sorry, something went wrong. Please try again or contact support.", "options": [], "links": []})
        bot_message = next_node.get("label", "")
        options = get_options(next_node)
        links = get_links(next_node)
        user_states[user_id] = next_id
        print(f"[DEBUG] Node ID: {next_id}, Links: {links}")
        return jsonify({"bot": bot_message, "options": options, "links": links})
    else:
        print(f"[DEBUG] Node ID: {current_node_id}, Links: {get_links(node)}")
        return jsonify({"bot": "Sorry, I didn't understand that.", "options": get_options(node), "links": get_links(node)})

@app.route("/")
def serve_chat():
    return render_template("chat.html")

if __name__ == "__main__":
    app.run(debug=True)
