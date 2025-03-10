import discord
from discord.ext import commands
from config import logger
import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Méthode commune pour ban et kick
    async def moderation_action(self, ctx, action, membre, raison):
        perms = ctx.guild.me.guild_permissions
        actions = {
            "kick": (perms.kick_members, membre.kick, "👢 Expulsé"),
            "ban": (perms.ban_members, membre.ban, "🔨 Banni"),
        }

        if not actions[action][0]:
            return await ctx.send(f"⛔ Je ne peux pas effectuer de {action}.")

        if membre.top_role >= ctx.author.top_role:
            return await ctx.send("⛔ Vous ne pouvez pas modérer ce membre.")

        try:
            await actions[action][1](reason=raison)
            await ctx.send(f"{actions[action][2]} {membre.mention} : {raison}")
            logger.info(f"{actions[action][2]} {membre} par {ctx.author}")
        except discord.HTTPException as e:
            await ctx.send(f"⛔ Erreur : {e}")

    @commands.hybrid_command(description="Expulse un membre.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, membre: discord.Member, *, raison="Non spécifiée"):
        await self.moderation_action(ctx, "kick", membre, raison)

    @commands.hybrid_command(description="Bannit un membre.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, membre: discord.Member, *, raison="Non spécifiée"):
        await self.moderation_action(ctx, "ban", membre, raison)

    @commands.hybrid_command(description="Débannit un utilisateur par ID.")
    @commands.has_permissions(ban_members=True)
    async def deban(self, ctx, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"🔓 {user.name} débanni avec succès.")
            logger.info(f"🔓 {user.name} débanni par {ctx.author}")
        except discord.NotFound:
            await ctx.send("⚠️ Utilisateur non trouvé ou pas banni.")
        except discord.HTTPException as e:
            await ctx.send(f"⛔ Erreur Discord : {e}")

    @commands.hybrid_command(description="Supprimer des messages du salon actuel.")
    @commands.has_permissions(manage_messages=True)
    @discord.app_commands.describe(
        nombre="Nombre de messages à supprimer (entre 1 et 1000). Par défaut 10 messages.",
        delai="Délai en secondes avant suppression (facultatif)."
    )
    async def clear(self, ctx, nombre: int = 10, delai: int = 0):
        await ctx.defer(ephemeral=True)

        limite = max(1, min(nombre, 1000))

        def is_not_pinned(msg):
            return not msg.pinned

        if delai > 0:
            confirmation = await ctx.send(f"⏳ Suppression des messages dans {delai} secondes...", ephemeral=True)
            await asyncio.sleep(delai)

        try:
            deleted = await ctx.channel.purge(limit=limite, check=is_not_pinned)
            confirmation_message = await ctx.send(f"✅ {len(deleted)} messages supprimés.", ephemeral=True)
            logger.info(f"🗑️ {len(deleted)} messages supprimés par {ctx.author} dans #{ctx.channel}.")

            await asyncio.sleep(30)
            await confirmation_message.delete()

        except discord.Forbidden:
            await ctx.send("⛔ Permissions insuffisantes pour supprimer des messages.", ephemeral=True)
            logger.warning(f"❌ Suppression échouée (permissions) par {ctx.author}.")
        except discord.HTTPException as e:
            await ctx.send(f"⚠️ Erreur Discord : {e}", ephemeral=True)
            logger.error(f"⚠️ Erreur pendant clear : {e}")

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⛔ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            logger.warning(f"🚫 Permission refusée pour {ctx.author} lors de l'utilisation de /clear.")
        else:
            await ctx.send(f"⚠️ Une erreur inattendue est survenue : {error}", ephemeral=True)
            logger.error(f"⚠️ Erreur inattendue dans clear : {error}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
