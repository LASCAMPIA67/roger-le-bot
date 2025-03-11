from flask import Flask
from threading import Thread
from werkzeug.serving import make_server
from config import logger

app = Flask(__name__)
server = None  # Variable globale pour le serveur Flask

@app.route('/')
def home():
    """Route principale pour indiquer que le bot est actif."""
    return "Le bot est en ligne !"

def run():
    """Lance le serveur Flask en mode bloquant."""
    global server
    logger.info("🚀 Démarrage du serveur Flask...")
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()

def keep_alive():
    """Lance le serveur Flask en arrière-plan sur un thread dédié."""
    thread = Thread(target=run, daemon=True)  # `daemon=True` permet d'éviter que le thread empêche l'arrêt du script
    thread.start()
    logger.info("✅ Serveur Flask lancé en arrière-plan.")

def stop_flask():
    """Arrête proprement le serveur Flask s'il est en cours d'exécution."""
    global server
    if server:
        logger.info("🛑 Arrêt du serveur Flask en cours...")
        server.shutdown()
        logger.info("✅ Serveur Flask arrêté proprement.")
    else:
        logger.warning("⚠️ Aucun serveur Flask en cours d'exécution.")
