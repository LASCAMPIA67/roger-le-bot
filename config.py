import logging
import colorlog
import os
from dotenv import load_dotenv

# ╔════════════════════════════════════════════════════════╗
# ║                  CHARGEMENT DES VARIABLES              ║
# ╚════════════════════════════════════════════════════════╝
if not load_dotenv():
    print("⚠️  Avertissement : Impossible de charger le fichier .env !")

# ╔════════════════════════════════════════════════════════╗
# ║                 CONFIGURATION DES LOGS                 ║
# ╚════════════════════════════════════════════════════════╝
def setup_logger(name="bot"):
    """ Configure un logger avec colorlog pour la console et un fichier de logs. """
    log_colors = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level, logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if not logger.hasHandlers():
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)s%(reset)s | %(message)s",
            log_colors=log_colors
        )

        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Handler fichier log
        file_handler = logging.FileHandler("bot.log", encoding="utf-8")
        file_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Filtrer les logs inutiles de discord.py
    for module in ("discord", "discord.http", "discord.gateway"):
        logging.getLogger(module).setLevel(logging.WARNING)

    return logger


# Initialisation du logger
logger = setup_logger()

# ╔════════════════════════════════════════════════════════╗
# ║                RÉCUPÉRATION DU TOKEN                   ║
# ╚════════════════════════════════════════════════════════╝
def get_token():
    """ Récupère et valide le token Discord depuis les variables d'environnement. """
    token = os.getenv("DISCORD_TOKEN")

    if not token or not isinstance(token, str) or "." not in token:
        logger.critical("❌ ERREUR : Token Discord invalide ou manquant dans le fichier .env !")
        raise ValueError("Le token Discord est absent ou incorrect. Vérifie ton fichier .env.")

    logger.info("✅ Token récupéré avec succès")
    return token
