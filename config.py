import logging
import colorlog
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
if not load_dotenv():
    print("⚠️  Avertissement : Impossible de charger le fichier .env !")

def setup_logger(name="bot"):
    """Configure un logger avec une sortie console colorée et un fichier de logs."""
    
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

    if not logger.hasHandlers():  # Évite d'ajouter plusieurs handlers si le logger existe déjà
        # Formatter coloré pour la console
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s | %(message)s",
            log_colors=log_colors
        )
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Formatter pour le fichier de logs
        log_filename = os.getenv("LOG_FILE", "bot.log")
        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        file_formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

# Initialisation du logger
logger = setup_logger()

def get_token():
    """Récupère et valide le token Discord depuis le fichier .env."""
    
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        logger.critical("❌ ERREUR : Le token Discord est manquant dans .env !")
        raise ValueError("Le token Discord est absent. Vérifiez le fichier .env.")

    # Vérification basique du format du token (évite les erreurs de connexion)
    if len(token.split(".")) < 3:
        logger.critical("❌ ERREUR : Token Discord invalide !")
        raise ValueError("Le token Discord est incorrect. Vérifiez votre bot sur https://discord.com/developers/applications.")

    logger.info("✅ Token Discord récupéré avec succès")
    return token
