from flask import Flask, render_template, request, jsonify, session
import subprocess, os, sys

# --- Flask setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
app.secret_key = "REPLACE_ME_WITH_SECRET"

# --- Game scripts mapping (MUST MATCH YOUR HTML SLUGS) ---
GAME_SCRIPTS = {
    "roulette": os.path.join(BASE_DIR, "roulette.py"),
    "rps": os.path.join(BASE_DIR, "rock paper scissors game.py"),
    "tetris": os.path.join(BASE_DIR, "tetris game.py"),
    "uno": os.path.join(BASE_DIR, "uno game.py"),
}

@app.before_request
def ensure_balance():
    if "balance" not in session:
        session["balance"] = 1000

# --- Routes ---

@app.route("/")
def index():
    # This must find templates/index.html
    print("Serving index.html from:", app.template_folder)
    return render_template("index.html")

@app.route("/api/run/<game>", methods=["POST"])
def run_game(game):
    # Debug print so you can see what the frontend sent
    print("Requested game slug:", repr(game))
    print("Available game keys:", list(GAME_SCRIPTS.keys()))

    if game not in GAME_SCRIPTS:
        return jsonify({"error": "Unknown game"}), 404

    script_path = GAME_SCRIPTS[game]
    if not os.path.exists(script_path):
        return jsonify({"error": f"Script not found: {script_path}"}), 404

    try:
        # Launch the game in a separate process, don't wait for it to finish
        subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return jsonify({"message": f"{game} launched", "launched": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("BASE_DIR:", BASE_DIR)
    print("Templates folder:", app.template_folder)
    app.run(debug=True, port=5000)
