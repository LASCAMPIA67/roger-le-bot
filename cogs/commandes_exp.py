import discord
from discord.ext import commands
import json
import os

class ExpCommands(commands.Cog):
    """Gestion des commandes liées à l'XP."""

    def __init__(self, bot):
        self.bot = bot
        self.file_path = "xp_data.json"
        self.load_xp_data()

    def load_xp_data(self):
        """Charge les données XP depuis un fichier JSON, avec gestion des erreurs."""
        try:
            if not os.path.exists(self.file_path):
                with open(self.file_path, "w") as f:
                    json.dump({}, f)

            with open(self.file_path, "r") as f:
                data = f.read().strip()
                self.xp_data = json.loads(data) if data else {}
        except (json.JSONDecodeError, FileNotFoundError):
            self.xp_data = {}
            self.save_xp_data()

    def save_xp_data(self):
        """Sauvegarde les données XP dans un fichier JSON."""
        with open(self.file_path, "w") as f:
            json.dump(self.xp_data, f, indent=4)

    @commands.hybrid_command(name="xp", description="Affiche votre niveau et votre XP actuel.")
    async def check_xp(self, ctx, member: discord.Member = None):
        """Commande pour voir son XP et son niveau."""
        self.load_xp_data()  # Recharge les données pour afficher des valeurs à jour
        member = member or ctx.author
        user_id = str(member.id)

        if user_id not in self.xp_data:
            await ctx.send(f"📉 {member.mention} n'a pas encore d'expérience.")
            return

        xp = self.xp_data[user_id]["xp"]
        level = self.xp_data[user_id]["level"]
        await ctx.send(f"📊 {member.mention} est au niveau **{level}** avec **{xp} XP**.")

async def setup(bot):
    """Ajoute le Cog au bot."""
    await bot.add_cog(ExpCommands(bot))
