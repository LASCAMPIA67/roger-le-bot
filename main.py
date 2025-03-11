import discord
import asyncio
import os
import shutil
from discord.ext import commands
from config import get_token, logger
from keep_alive import keep_alive, stop_flask

class Bot(commands.Bot):
    """Classe principale du bot avec gestion améliorée des cogs et des événements."""

    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=os.getenv("BOT_PREFIX", "!"), intents=intents)

    @property
    def cogs_list(self):
        """Retourne la liste des Cogs à charger."""
        return [
            "cogs.events",
            "cogs.commandes_moderation",
            "cogs.commandes_reseau",
            "cogs.exp",
            "cogs.commandes_exp",
            "cogs.commandes_utiles",
            "cogs.creator"
        ]

    async def setup_hook(self):
        """Charge tous les Cogs au démarrage."""
        logger.info("🚀 Initialisation des cogs...")
        for ext in self.cogs_list:
            try:
                await self.load_extension(ext)
                logger.info(f"✅ Cog chargé : {ext}")
            except Exception as e:
                logger.error(f"❌ Erreur lors du chargement du cog {ext} : {e}", exc_info=True)
        logger.info("✅ Tous les cogs ont été chargés avec succès.")

    async def on_ready(self):
        """Affiche un message quand le bot est prêt."""
        logger.info(f"✅ Connecté en tant que {self.user} - ID: {self.user.id}")
        logger.info("🔹 Bot prêt à recevoir des commandes.")

    async def close(self):
        """Gère la fermeture propre du bot et du serveur Flask."""
        logger.warning("🛑 Arrêt du bot...")
        stop_flask()  # Arrête le serveur Flask avant la fermeture du bot
        await super().close()
        self.cleanup_pycache()

    def cleanup_pycache(self):
        """Supprime les fichiers '__pycache__' pour éviter l'accumulation de fichiers inutiles."""
        logger.info("🧹 Suppression des anciens fichiers __pycache__...")
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
    """Démarre le bot avec une gestion améliorée des erreurs et un keep-alive actif."""
    try:
        logger.info("🚀 Démarrage du bot...")
        keep_alive()  # Lancer le serveur Flask pour garder le bot actif
        await bot.start(get_token())

    except discord.LoginFailure:
        logger.critical("❌ ERREUR : Token Discord invalide ou désactivé.")
    except asyncio.TimeoutError:
        logger.critical("❌ ERREUR : Impossible de se connecter à Discord (Timeout).")
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.warning("🛑 Arrêt demandé par l'utilisateur.")
    except Exception as e:
        logger.critical(f"❌ Erreur critique inattendue : {e}", exc_info=True)
    finally:
        await bot.close()
        logger.info("🔴 Bot fermé proprement.")

if __name__ == "__main__":
    asyncio.run(main())
