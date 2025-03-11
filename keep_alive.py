from flask import Flask
from threading import Thread
from werkzeug.serving import make_server
from config import logger

app = Flask(__name__)
server = None  # Variable globale pour le serveur Flask

@app.route('/')
def home():
    return "Le bot est en ligne !"

def run():
    global server
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()

def keep_alive():
    """Lance le serveur Flask en arrière-plan."""
    thread = Thread(target=run)
    thread.start()

def stop_flask():
    """Arrête proprement le serveur Flask."""
    if server:
        server.shutdown()
        logger.info(f"🛑 Serveur Flask arrêté proprement.")
