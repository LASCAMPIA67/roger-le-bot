import discord
import asyncio
from discord.ext import commands
from config import get_token, logger
from rich.console import Console

console = Console()

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.guilds = True
        super().__init__(command_prefix='!', intents=intents)

    @property
    def cogs_list(self):
        """Liste complète et à jour des cogs."""
        return [
            "cogs.events",
            "cogs.commandes_moderation",
            "cogs.commandes_reseau",
            "cogs.commandes_jeux"
        ]

    async def setup_hook(self):
        logger.info("🚀 Démarrage de setup_hook...")
        for ext in self.cogs_list:
            try:
                await self.load_extension(ext)
                logger.info(f"✅ Cog chargé : {ext}")
            except Exception as e:
                logger.error(f"❌ Erreur chargement du cog {ext} : {e}", exc_info=True)

        logger.info("✅ Fin du setup_hook.")

bot = Bot()

async def main():
    try:
        async with bot:
            await bot.start(get_token())
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.warning("🛑 Arrêt demandé par l'utilisateur.")
    except discord.LoginFailure:
        logger.critical("❌ Token Discord invalide !")
    except Exception as e:
        logger.critical(f"❌ Erreur critique inattendue : {e}")
    finally:
        await bot.close()
        logger.info("🔴 Bot fermé proprement.")

if __name__ == "__main__":
    asyncio.run(main())