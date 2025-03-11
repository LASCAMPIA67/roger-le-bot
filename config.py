import logging
import colorlog
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
if not load_dotenv():
    print("⚠️  Avertissement : Impossible de charger le fichier .env !")

# Configuration des logs
def setup_logger(name="bot"):
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

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler("bot.log", encoding="utf-8")
        file_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

logger = setup_logger()

# Récupération du token Discord
def get_token():
    token = os.getenv("DISCORD_TOKEN")
    if not token or len(token.split(".")) < 3:
        logger.critical("❌ ERREUR : Token Discord invalide ou manquant dans .env !")
        raise ValueError("Le token Discord est absent ou incorrect. Vérifiez le fichier .env.")
    logger.info("✅ Token Discord récupéré avec succès")
    return token
