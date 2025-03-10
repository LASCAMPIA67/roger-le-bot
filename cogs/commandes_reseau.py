import aiohttp
from discord.ext import commands
from config import logger

class Reseau(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(description="Affiche votre adresse IP publique.")
    async def monip(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://api64.ipify.org?format=json") as resp:
                    data = await resp.json()
                    ip = data.get("ip")
                    if ip:
                        await ctx.send(f"🌐 Votre IP publique est : `{ip}`", ephemeral=True)
                        logger.info(f"🌐 IP récupérée pour {ctx.author}: {ip}")
                    else:
                        await ctx.send("⚠️ Impossible de récupérer l'IP.", ephemeral=True)
            except Exception as e:
                await ctx.send(f"⚠️ Erreur : {e}", ephemeral=True)
                logger.error(f"Erreur récupération IP : {e}")

    @commands.hybrid_command(description="Affiche la latence du bot.")
    async def ping(self, ctx: commands.Context):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong ! Latence : `{latency} ms`")
        logger.info(f"🏓 Latence : {latency} ms (par {ctx.author})")

async def setup(bot: commands.Bot):
    await bot.add_cog(Reseau(bot))
