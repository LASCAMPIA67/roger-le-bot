import discord
from discord import app_commands
from discord.ext import commands
from config import logger
import json
import os
from collections import defaultdict

class ExpCommands(commands.Cog):
    """Cog pour les commandes liées à l'XP des utilisateurs."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.xp_data = defaultdict(lambda: {"xp": 0, "level": 1})  # Utilisation de defaultdict pour gérer les données par défaut
        # N'appelez pas load_xp_data() dans __init__ mais dans la méthode setup

    async def load_xp_data(self):
        """Charge les données d'XP depuis le fichier xp_data.json."""
        if os.path.exists("xp_data.json"):
            try:
                with open("xp_data.json", "r") as f:
                    self.xp_data.update(json.load(f))
            except Exception as e:
                logger.error(f"Erreur lors du chargement des données d'XP : {e}")

    async def save_xp_data(self):
        """Sauvegarde les données d'XP dans le fichier xp_data.json."""
        try:
            with open("xp_data.json", "w") as f:
                json.dump(self.xp_data, f, indent=4)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données d'XP : {e}")

    @app_commands.command(name="ajouter_xp", description="Ajoute de l'XP à un utilisateur.")
    @app_commands.checks.has_permissions(administrator=True)  # Seuls les admins peuvent utiliser cette commande
    async def add_xp(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        """
        Ajoute un montant spécifique d'XP à un utilisateur. Seuls les administrateurs peuvent utiliser cette commande.
        """
        # Vérification que le montant d'XP est positif
        if amount <= 0:
            await interaction.response.send_message(
                "⚠️ L'XP ajoutée doit être un nombre positif.", ephemeral=True
            )
            return

        # Ajout de l'XP
        user_id = str(member.id)
        self.xp_data[user_id]["xp"] += amount

        # Sauvegarde des données d'XP
        try:
            await self.save_xp_data()
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données d'XP: {e}")
            await interaction.response.send_message(
                "⚠️ Une erreur est survenue lors de la sauvegarde des données d'XP.", ephemeral=True
            )
            return

        # Confirmation de l'ajout d'XP
        logger.info(f"✅ {amount} XP ajoutés à {member.name} (ID: {member.id}) par {interaction.user.name}.")
        await interaction.response.send_message(
            f"✅ {amount} XP ajoutés à {member.mention} !", ephemeral=True
        )

    @app_commands.command(name="exp", description="Affiche l'XP d'un utilisateur.")
    async def exp(self, interaction: discord.Interaction, member: discord.Member = None):
        """
        Affiche l'XP d'un utilisateur. Si aucun membre n'est mentionné, affiche l'XP de l'utilisateur qui a invoqué la commande.
        """
        if member is None:
            member = interaction.user  # Si aucun membre n'est spécifié, on affiche l'XP de l'utilisateur ayant invoqué la commande

        user_id = str(member.id)
        xp_data = self.xp_data[user_id]  # Données d'XP récupérées directement, car defaultdict s'en charge

        xp = xp_data["xp"]
        level = xp_data["level"]

        # Envoi d'un message avec l'XP et le niveau du membre
        await interaction.response.send_message(
            f"📊 {member.mention} a {xp} XP et est au niveau {level}.",
            ephemeral=True  # Réponse éphémère pour qu'elle soit visible uniquement par l'utilisateur
        )

    @app_commands.command(name="classement", description="Affiche le classement des utilisateurs par XP.")
    async def classement(self, interaction: discord.Interaction):
        """
        Affiche le classement des utilisateurs en fonction de leur XP.
        """
        # Trie les utilisateurs en fonction de leur XP, du plus haut au plus bas
        sorted_xp = sorted(self.xp_data.items(), key=lambda x: x[1]["xp"], reverse=True)

        if not sorted_xp:
            await interaction.response.send_message("⚠️ Aucun utilisateur avec de l'XP n'a été trouvé.", ephemeral=True)
            return

        # Construction du message du classement
        ranking_message = "🏆 **Classement des utilisateurs par XP :**\n"
        for idx, (user_id, data) in enumerate(sorted_xp[:10], start=1):  # Affichage des 10 premiers
            try:
                member = await interaction.guild.fetch_member(int(user_id))
                ranking_message += f"{idx}. {member.mention} - {data['xp']} XP (Niveau {data['level']})\n"
            except discord.NotFound:
                continue  # Ignore si un utilisateur est introuvable

        # Envoi du classement
        await interaction.response.send_message(ranking_message, ephemeral=True)

async def setup(bot: commands.Bot):
    """Ajoute le Cog au bot."""
    cog = ExpCommands(bot)
    await cog.load_xp_data()  # Charge les données d'XP lors de l'ajout du Cog
    await bot.add_cog(cog)
