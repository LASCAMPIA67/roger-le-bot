import discord
from discord.ext import commands
from config import logger

class Events(commands.Cog):
    """Gestion des événements du bot Discord."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ready_triggered = False

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Événement déclenché lorsque le bot est prêt."""
        if self.ready_triggered:
            return
        self.ready_triggered = True

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Répond 'Bonjour' si un utilisateur dit 'bonjour'."""
        if message.author.bot or not message.guild:
            return

        if message.content.lower().startswith("bonjour"):
            if message.channel.permissions_for(message.guild.me).send_messages:
                await message.channel.send("👋 Bonjour, c'est le bot !")
                logger.info(f"👋 Réponse envoyée à {message.author.display_name}")

        await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        """Annonce la suppression d'un message."""
        if not message.guild or not message.content:
            return

        truncated_content = message.content[:50] + ("..." if len(message.content) > 50 else "")
        logger.info(f"🗑️ Message supprimé par {message.author.display_name} : {truncated_content}")

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        """Annonce la modification d'un message."""
        if not before.guild or before.content == after.content:
            return

        if before.channel.permissions_for(before.guild.me).send_messages:
            before_content = before.content[:50] + ("..." if len(before.content) > 50 else "")
            after_content = after.content[:50] + ("..." if len(after.content) > 50 else "")
            await after.channel.send(f"✏️ {before_content} → {after_content}")
            logger.info(f"✏️ Message modifié par {before.author.display_name} : '{before_content}' → '{after_content}'")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Souhaite la bienvenue aux nouveaux membres."""
        channel = discord.utils.get(member.guild.text_channels, name="bienvenue")
        if channel and channel.permissions_for(member.guild.me).send_messages:
            embed = discord.Embed(
                title="🎉 Bienvenue !",
                description=f"Bienvenue sur le serveur, {member.mention} !",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)
            logger.info(f"🟢 {member.display_name} a rejoint le serveur.")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        """Gère le départ d'un membre (banni ou départ volontaire)."""
        if member.bot:
            return

        try:
            await member.guild.fetch_ban(member)
            logger.info(f"🚫 {member.display_name} a été banni (ignore message départ).")
            return
        except discord.NotFound:
            pass
        except discord.Forbidden:
            logger.warning("⚠️ Permissions insuffisantes pour vérifier les bannissements.")
            return

        channel = discord.utils.get(member.guild.text_channels, name="départs")
        if channel and channel.permissions_for(member.guild.me).send_messages:
            embed = discord.Embed(
                title="😢 Au revoir !",
                description=f"{member.mention} a quitté le serveur.",
                color=discord.Color.red()
            )
            await channel.send(embed=embed)

        logger.warning(f"🚪 {member.display_name} a quitté le serveur (non banni).")

async def setup(bot: commands.Bot) -> None:
    """Ajoute la classe Events comme un Cog dans le bot."""
    await bot.add_cog(Events(bot))
