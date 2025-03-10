import discord
import asyncio
import os
import shutil
from discord.ext import commands
from config import get_token, logger
from rich.console import Console

console = Console()

class Bot(commands.Bot):
    """Classe principale du bot avec gestion améliorée des cogs."""

    def __init__(self):
        intents = discord.Intents.all()  # Active tous les intents
        super().__init__(command_prefix='!', intents=intents)

    @property
    def cogs_list(self):
        """Retourne la liste complète et à jour des cogs."""
        return [
            "cogs.events",
            "cogs.commandes_moderation",
            "cogs.commandes_reseau",
            "cogs.commandes_jeux",
            "cogs.exp",
            "cogs.commandes_exp"
        ]

    async def setup_hook(self):
        """Charge les cogs au démarrage du bot."""
        logger.info("🚀 Initialisation des cogs...")
        for ext in self.cogs_list:
            try:
                await self.load_extension(ext)
                logger.info(f"✅ Cog chargé : {ext}")
            except Exception as e:
                logger.error(f"❌ Erreur lors du chargement du cog {ext} : {e}", exc_info=True)

        logger.info("✅ Tous les cogs ont été chargés avec succès.")

    async def close(self):
        """Gère la fermeture propre du bot."""
        logger.warning("🛑 Arrêt du bot...")
        await super().close()
        self.cleanup_pycache()  # Supprime les fichiers inutiles

    def cleanup_pycache(self):
        """Supprime tous les dossiers __pycache__ après l'arrêt du bot."""
        logger.info("🧹 Suppression des anciens dossiers __pycache__...")
        for root, dirs, _ in os.walk(".", topdown=False):
            for d in dirs:
                if d == "__pycache__":
                    pycache_path = os.path.join(root, d)
                    try:
                        shutil.rmtree(pycache_path)
                        logger.info(f"✅ Dossier supprimé : {pycache_path}")
                    except Exception as e:
                        logger.error(f"❌ Erreur lors de la suppression de {pycache_path} : {e}")

        logger.info("🔴 Nettoyage terminé.")

bot = Bot()

async def main():
    """Démarre le bot avec une gestion améliorée des erreurs."""
    try:
        logger.info("🚀 Démarrage du bot...")
        await bot.start(get_token())

    except discord.LoginFailure:
        logger.critical("❌ ERREUR : Le token Discord est invalide ou désactivé.")
        return  # Empêche le bot de continuer

    except asyncio.TimeoutError:
        logger.critical("❌ ERREUR : Impossible de se connecter à Discord (Timeout).")
        return  # Le bot s'arrête proprement

    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.warning("🛑 Arrêt demandé par l'utilisateur.")

    except Exception as e:
        logger.critical(f"❌ Erreur critique inattendue : {e}", exc_info=True)

    finally:
        await bot.close()  # Nettoyage et fermeture propre
        logger.info("🔴 Bot fermé proprement.")

if __name__ == "__main__":
    asyncio.run(main())
