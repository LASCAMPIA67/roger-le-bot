import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from config import logger

class Reseau(commands.Cog):
    """Cog gérant les commandes réseau du bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = None  # La session sera créée dans `cog_load`

    async def cog_load(self):
        """Crée une session HTTP lors du chargement du cog."""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5))
        logger.info("✅ Session HTTP créée pour le cog Reseau.")

    async def cog_unload(self):
        """Ferme proprement la session HTTP lors du retrait du Cog."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("🛑 Session HTTP fermée.")

    def check_session(self):
        """Vérifie que la session HTTP est bien active."""
        if not self.session or self.session.closed:
            logger.error("❌ Tentative d'utilisation de `monip` sans session HTTP active.")
            return False
        return True

    @app_commands.command(name="monip", description="Affiche votre adresse IP publique.")
    async def monip(self, interaction: discord.Interaction):
        """Commande pour récupérer et afficher l'adresse IP publique."""
        if not self.check_session():
            await interaction.response.send_message(
                "⚠️ Erreur interne : la session HTTP est fermée.", ephemeral=True
            )
            return

        url = "https://api64.ipify.org?format=json"

        try:
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    logger.warning(f"❌ Échec de récupération de l'IP (statut HTTP {resp.status})")
                    await interaction.response.send_message(
                        "⚠️ Impossible de récupérer l'IP. Réessayez plus tard.", ephemeral=True
                    )
                    return

                data = await resp.json()
                ip = data.get("ip")

                if not ip:
                    await interaction.response.send_message(
                        "⚠️ Impossible de récupérer l'IP.", ephemeral=True
                    )
                    return

                response_message = f"🌐 Votre IP publique est : `{ip}`"
                await interaction.response.send_message(response_message, ephemeral=True)  # Rendre ce message éphémère
                logger.info(f"🌐 IP récupérée pour {interaction.user}: {ip}")

        except aiohttp.ClientConnectionError:
            logger.error("❌ Erreur de connexion lors de la récupération de l'IP.")
            await interaction.response.send_message(
                "⚠️ Impossible de contacter le serveur. Vérifiez votre connexion.", ephemeral=True
            )
        except aiohttp.ClientTimeout:
            logger.error("❌ Timeout lors de la récupération de l'IP.")
            await interaction.response.send_message(
                "⚠️ Le serveur met trop de temps à répondre. Réessayez plus tard.", ephemeral=True
            )
        except aiohttp.ContentTypeError:
            logger.error("❌ Erreur lors de la lecture de la réponse JSON.")
            await interaction.response.send_message(
                "⚠️ Erreur de format des données reçues.", ephemeral=True
            )
        except Exception as e:
            logger.error(f"❌ Erreur inattendue lors de la récupération de l'IP : {e}")
            await interaction.response.send_message(
                "⚠️ Une erreur est survenue.", ephemeral=True
            )

    @app_commands.command(name="ping", description="Affiche la latence du bot.")
    async def ping(self, interaction: discord.Interaction):
        """Commande qui affiche la latence du bot."""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong ! Latence : `{latency} ms`", ephemeral=True)  # Rendre ce message éphémère
        logger.info(f"🏓 Latence : {latency} ms (par {interaction.user})")

async def setup(bot: commands.Bot):
    """Ajoute le cog Reseau au bot."""
    await bot.add_cog(Reseau(bot))
