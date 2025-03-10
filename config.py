import logging
import colorlog
import os
from dotenv import load_dotenv

# ╔════════════════════════════════════════════════════════╗
# ║                  CHARGEMENT DES VARIABLES              ║
# ╚════════════════════════════════════════════════════════╝
load_dotenv()

# ╔════════════════════════════════════════════════════════╗
# ║                 CONFIGURATION DES LOGS                 ║
# ╚════════════════════════════════════════════════════════╝
def setup_logger():
    """ Configure le système de logs avec colorlog pour la console et un fichier de logs. """
    log_colors = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }

    # Définition du niveau de log (modifiable via .env)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level, logging.INFO)

    # Formatter coloré pour la console
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s%(reset)s | %(message)s",
        log_colors=log_colors
    )

    # Création du logger
    logger = logging.getLogger("bot")
    logger.setLevel(log_level)

    # Vérification pour éviter d'ajouter plusieurs handlers en cas d'import multiple
    if not logger.hasHandlers():
        # Handler pour la console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Handler pour fichier de logs
        file_handler = logging.FileHandler("bot.log", encoding="utf-8")
        file_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Filtrage des logs inutiles de discord.py
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("discord.http").setLevel(logging.WARNING)
    logging.getLogger("discord.gateway").setLevel(logging.WARNING)

    return logger


# Initialisation du logger
logger = setup_logger()

# ╔════════════════════════════════════════════════════════╗
# ║                RÉCUPÉRATION DU TOKEN                   ║
# ╚════════════════════════════════════════════════════════╝
def get_token():
    """ Récupère le token Discord depuis les variables d'environnement. """
    token = os.getenv("DISCORD_TOKEN")

    if not token or not isinstance(token, str) or len(token) < 50:  # Les tokens font en général 59 caractères
        logger.critical("❌ ERREUR : Le token Discord est manquant ou invalide dans le fichier .env !")
        raise ValueError("Le token Discord est absent ou incorrect. Vérifie ton fichier .env.")

    logger.info("✅ Token récupéré avec succès")
    return token
