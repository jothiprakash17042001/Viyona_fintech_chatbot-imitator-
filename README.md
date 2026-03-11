# Viyona Fintech Chatbot

A simple Flask-based chatbot demo that drives conversation based on `flow.json`.

## ✅ Quick Start (Windows)

1. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Run the app:

   ```powershell
   python app.py
   ```

4. Open a browser and visit:

   ```text
   http://127.0.0.1:5000/
   ```

---

## 📌 Project structure

- `app.py` - Flask backend serving the chat flow and frontend
- `flow.json` - Flow definition used by the chatbot logic
- `templates/index.html` - Frontend UI template
- `static/script.js` - Client-side chat logic
- `static/style.css` - UI styling

---

## 🛠️ Notes

- The chatbot uses a simple JSON flow and matches user input to button values.
- The UI is hidden by default and is opened by clicking the bot icon.
