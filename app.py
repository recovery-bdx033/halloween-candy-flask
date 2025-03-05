from flask import Flask, render_template
import sys
import subprocess
import os
import signal

app = Flask(__name__)
process = None  # Variable pour stocker le processus du jeu

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-game')
def start_game():
    global process
    try:
        if sys.platform == "win32":
            process = subprocess.Popen(["python", "main.py"], shell=True)
        else:
            process = subprocess.Popen(["python3", "main.py"])
        print("[LOG] Jeu lancé depuis Flask")
        return "Le jeu a démarré !"
    except Exception as e:
        print(f"[ERROR] Erreur lors du démarrage du jeu : {e}")
        return f"Erreur : {e}"

@app.route('/stop-game')
def stop_game():
    global process
    if process:
        if sys.platform == "win32":
            subprocess.call(["taskkill", "/F", "/PID", str(process.pid)], shell=True)  # Windows
        else:
            os.kill(process.pid, signal.SIGTERM)  # Linux/macOS

        process = None
        print("[LOG] Jeu arrêté depuis Flask")
        return "Le jeu a été arrêté !"
    else:
        return "Aucun jeu en cours."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
