import discord
from discord.ext import commands
from config import logger

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ready_triggered = False

    @commands.Cog.listener()
    async def on_ready(self):
        if self.ready_triggered:
            return
        self.ready_triggered = True

        logger.info(f"✅ {self.bot.user} connecté à {len(self.bot.guilds)} serveur(s).")
        synced = await self.bot.tree.sync()
        logger.info(f"🔄 {len(synced)} commande(s) synchronisée(s).")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if message.content.lower().startswith("bonjour"):
            if message.channel.permissions_for(message.guild.me).send_messages:
                await message.channel.send("👋 Bonjour, c'est le bot !")
                logger.info(f"👋 Réponse envoyée à {message.author.name}")

        await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild or not message.content:
            return

        if message.channel.permissions_for(message.guild.me).send_messages:
            content = message.content[:50] + ("..." if len(message.content) > 50 else "")
            await message.channel.send(f"🗑️ {message.author.name} a supprimé : {content}")
            logger.info(f"🗑️ Message supprimé par {message.author.name} : {content}")

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not before.guild or before.content == after.content:
            return

        if before.channel.permissions_for(before.guild.me).send_messages:
            before_content = before.content[:50] + ("..." if len(before.content) > 50 else "")
            after_content = after.content[:50] + ("..." if len(after.content) > 50 else "")
            await after.channel.send(f"✏️ {before_content} → {after_content}")
            logger.info(f"✏️ Message modifié par {before.author.name} : '{before_content}' → '{after_content}'")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = discord.utils.get(member.guild.text_channels, name="bienvenue")
        if channel and channel.permissions_for(member.guild.me).send_messages:
            embed = discord.Embed(
                title="🎉 Bienvenue !",
                description=f"Bienvenue sur le serveur, {member.mention} !",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)
            logger.info(f"🟢 {member} a rejoint le serveur.")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.bot:
            return

        try:
            await member.guild.fetch_ban(member)
            logger.info(f"🚫 {member} a été banni (ignore message départ).")
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

        logger.warning(f"🚪 {member} a quitté le serveur (non banni).")

async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
