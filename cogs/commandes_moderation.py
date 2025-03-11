import discord
import asyncio
from discord import app_commands
from discord.ext import commands
from config import logger

class Moderation(commands.Cog):
    """Cog contenant les commandes de modération."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def moderation_action(self, interaction: discord.Interaction, action: str, membre: discord.Member, raison: str):
        """Méthode commune pour les actions de modération (kick et ban)."""
        if not interaction.guild:
            return await interaction.response.send_message("⛔ Cette commande ne peut être utilisée que sur un serveur.", ephemeral=True)

        actions = {
            "kick": {
                "perm": interaction.guild.me.guild_permissions.kick_members,
                "method": membre.kick,
                "emoji": "👢",
                "msg": "Expulsé"
            },
            "ban": {
                "perm": interaction.guild.me.guild_permissions.ban_members,
                "method": membre.ban,
                "emoji": "🔨",
                "msg": "Banni"
            }
        }

        if action not in actions:
            return await interaction.response.send_message("⛔ Action inconnue.", ephemeral=True)

        act = actions[action]

        # Vérification des permissions du bot
        if not act["perm"]:
            return await interaction.response.send_message(f"⛔ Je n'ai pas la permission de {action} ce membre.", ephemeral=True)

        # Vérification de la hiérarchie des rôles
        if membre.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("⛔ Vous ne pouvez pas modérer un membre avec un rôle égal ou supérieur au vôtre.", ephemeral=True)

        if membre == interaction.user:
            return await interaction.response.send_message("⛔ Vous ne pouvez pas vous modérer vous-même.", ephemeral=True)

        try:
            await act["method"](reason=raison)
            await interaction.response.send_message(f"{act['emoji']} {membre.mention} {act['msg']} pour : {raison}")
            logger.info(f"{act['emoji']} {membre} {act['msg']} par {interaction.user} - Raison : {raison}")
        except discord.Forbidden:
            await interaction.response.send_message("⛔ Je n'ai pas la permission de faire cela.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"⚠️ Erreur Discord : {e}", ephemeral=True)
            logger.error(f"⚠️ Erreur Discord lors de {action} {membre}: {e}")

    @app_commands.command(name="kick", description="Expulse un membre.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, membre: discord.Member, raison: str = "Non spécifiée"):
        """Expulse un membre du serveur."""
        await self.moderation_action(interaction, "kick", membre, raison)

    @app_commands.command(name="ban", description="Bannit un membre.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, membre: discord.Member, raison: str = "Non spécifiée"):
        """Bannit un membre du serveur."""
        await self.moderation_action(interaction, "ban", membre, raison)

    @app_commands.command(name="deban", description="Débannit un utilisateur par ID.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def deban(self, interaction: discord.Interaction, user_id: int):
        """Débannit un utilisateur via son ID."""
        if not interaction.guild:
            return await interaction.response.send_message("⛔ Cette commande ne peut être utilisée que sur un serveur.", ephemeral=True)
        try:
            user = await self.bot.fetch_user(user_id)
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"🔓 {user.name} a été débanni avec succès.")
            logger.info(f"🔓 {user.name} débanni par {interaction.user}")
        except discord.NotFound:
            await interaction.response.send_message("⚠️ Utilisateur non trouvé ou pas banni.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"⛔ Erreur Discord : {e}", ephemeral=True)
            logger.error(f"⚠️ Erreur Discord lors du débannissement de {user_id}: {e}")

    @app_commands.command(name="clear", description="Supprime des messages du salon actuel.")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(nombre="Nombre de messages à supprimer (entre 1 et 100).")
    async def clear(self, interaction: discord.Interaction, nombre: int = 100):
        """Supprime un nombre défini de messages."""
        await interaction.response.defer(ephemeral=True)  # Empêche l'expiration de l'interaction

        nombre = max(1, min(nombre, 100))  # Discord limite la purge à 100 messages

        def is_not_pinned(msg):
            return not msg.pinned  # On ne supprime pas les messages épinglés

        try:
            deleted = await interaction.channel.purge(limit=nombre, check=is_not_pinned)
            await interaction.followup.send(f"✅ {len(deleted)} messages supprimés.", ephemeral=True)
            logger.info(f"🗑️  {len(deleted)} messages supprimés par {interaction.user} dans #{interaction.channel}")

        except discord.Forbidden:
            await interaction.followup.send("⛔ Permissions insuffisantes pour supprimer des messages.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"⚠️ Erreur Discord : {e}", ephemeral=True)
            logger.error(f"⚠️ Erreur Discord lors de la suppression de messages: {e}")

    @clear.error
    async def clear_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Gestion des erreurs pour la commande clear."""
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("⛔ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            logger.warning(f"🚫 Permission refusée pour {interaction.user} lors de l'utilisation de /clear.")
        else:
            await interaction.response.send_message(f"⚠️ Une erreur inattendue est survenue : {error}", ephemeral=True)
            logger.error(f"⚠️ Erreur inattendue dans clear : {error}")

async def setup(bot: commands.Bot):
    """Ajoute le cog de modération au bot."""
    await bot.add_cog(Moderation(bot))
