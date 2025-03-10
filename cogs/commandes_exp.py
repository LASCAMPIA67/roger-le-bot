import discord
import json
import os
import asyncio
import aiofiles  # 📌 Importation pour une gestion asynchrone des fichiers
from discord import app_commands
from discord.ext import commands
from config import logger  # ✅ Importation du logger

class ExpCommands(commands.Cog):
    """Gestion des commandes liées à l'XP."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.file_path = "xp_data.json"
        self.lock = asyncio.Lock()  # Verrou pour éviter la corruption du fichier
        self.xp_data = {}  # Chargé à l'initialisation

    @commands.Cog.listener()
    async def on_ready(self):
        """Charge les données XP une fois que le bot est prêt."""
        self.xp_data = await self.load_xp_data()
        logger.info("✅ Données XP chargées avec succès.")

    async def load_xp_data(self):
        """Charge les données XP depuis un fichier JSON de manière asynchrone."""
        if not os.path.exists(self.file_path):
            return {}

        try:
            async with self.lock:
                async with aiofiles.open(self.file_path, "r", encoding="utf-8") as f:
                    data = await f.read()
                    return json.loads(data) if data else {}
        except json.JSONDecodeError:
            logger.warning("⚠️ Fichier XP corrompu, réinitialisation.")
            return {}
        except FileNotFoundError:
            logger.warning("⚠️ Fichier XP inexistant, création d'un nouveau fichier.")
            return {}
        except Exception as e:
            logger.error(f"⚠️ Erreur lors du chargement des données XP : {e}")
            return {}

    async def save_xp_data(self):
        """Sauvegarde les données XP dans un fichier JSON de manière asynchrone."""
        try:
            async with self.lock:
                async with aiofiles.open(self.file_path, "w", encoding="utf-8") as f:
                    await f.write(json.dumps(self.xp_data, indent=4))
            logger.info("✅ Données XP sauvegardées avec succès.")
        except Exception as e:
            logger.error(f"⚠️ Erreur lors de la sauvegarde des données XP : {e}")

    # 📌 Commande pour voir son XP et son niveau
    @app_commands.command(name="xp", description="Affiche votre niveau et votre XP actuel.")
    async def check_xp(self, interaction: discord.Interaction, member: discord.Member = None):
        """Commande pour voir son XP et son niveau."""
        member = member or interaction.user
        user_id = str(member.id)

        xp_data = self.xp_data.get(user_id, {"xp": 0, "level": 1})
        xp, level = xp_data["xp"], xp_data["level"]

        message = f"📊 {member.mention} est au **niveau {level}** avec **{xp} XP**."
        await interaction.response.send_message(message)

    # 📌 Commande pour ajouter de l'XP à un utilisateur
    @app_commands.command(name="ajouter_xp", description="Ajoute de l'XP à un utilisateur.")
    @app_commands.checks.has_permissions(administrator=True)  # Seuls les admins peuvent utiliser cette commande
    async def add_xp(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        """Ajoute un montant spécifique d'XP à un utilisateur."""
        if amount <= 0:
            await interaction.response.send_message("⚠️ L'XP ajoutée doit être un nombre positif.", ephemeral=True)
            return

        user_id = str(member.id)
        self.xp_data.setdefault(user_id, {"xp": 0, "level": 1})
        self.xp_data[user_id]["xp"] += amount

        await self.save_xp_data()  # Sauvegarde asynchrone
        logger.info(f"✅ {amount} XP ajoutés à {member.name} (ID: {member.id}) par {interaction.user.name}.")
        await interaction.response.send_message(f"✅ {amount} XP ajoutés à {member.mention} !")

async def setup(bot: commands.Bot):
    """Ajoute le Cog au bot."""
    await bot.add_cog(ExpCommands(bot))
