import discord
from discord import app_commands
from discord.ext import commands
import json
import os

class ExpCommands(commands.Cog):
    """Gestion de l'XP, des niveaux et des prestiges des utilisateurs."""

    FILE_PATH = "xp_data.json"

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.xp_data = {}
        self.load_xp_data()

    def load_xp_data(self):
        """Charge les données d'XP de manière sécurisée."""
        if os.path.exists(self.FILE_PATH):
            try:
                with open(self.FILE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.xp_data = data if isinstance(data, dict) else {}
            except (json.JSONDecodeError, FileNotFoundError):
                print("❌ Erreur: Impossible de charger xp_data.json. Réinitialisation.")
                self.xp_data = {}
                self.save_xp_data()

    def save_xp_data(self):
        """Sauvegarde les données XP de manière sécurisée."""
        try:
            with open(self.FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.xp_data, f, indent=4)
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde des données d'XP : {e}")

    def get_user_data(self, user_id: str):
        """Retourne les données XP de l'utilisateur ou les initialise."""
        if user_id not in self.xp_data:
            self.xp_data[user_id] = {"xp": 0, "level": 1, "prestige": 0}
        return self.xp_data[user_id]

    @app_commands.command(name="ajouter_xp", description="Ajoute de l'XP à un utilisateur.")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_xp(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        """Ajoute un montant spécifique d'XP à un utilisateur."""
        await interaction.response.defer(ephemeral=True)

        if amount <= 0:
            await interaction.followup.send("⚠️ L'XP doit être un nombre positif.", ephemeral=True)
            return

        user_id = str(member.id)
        user_data = self.get_user_data(user_id)
        user_data["xp"] += amount
        self.save_xp_data()

        await interaction.followup.send(f"✅ {amount} XP ajoutés à {member.mention} !", ephemeral=True)

    @app_commands.command(name="exp", description="Affiche l'XP d'un utilisateur.")
    async def exp(self, interaction: discord.Interaction, member: discord.Member = None):
        """Affiche l'XP d'un utilisateur."""
        await interaction.response.defer(ephemeral=True)

        member = member or interaction.user
        user_id = str(member.id)
        xp_data = self.get_user_data(user_id)

        embed = discord.Embed(title=f"📊 Statistiques de {member.display_name}", color=discord.Color.blue())
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="🆙 Niveau", value=str(xp_data["level"]), inline=True)
        embed.add_field(name="⭐ Prestige", value=str(xp_data["prestige"]), inline=True)
        embed.add_field(name="📈 XP", value=f"{xp_data['xp']}", inline=True)

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="classement", description="Affiche le classement des utilisateurs par XP et prestige.")
    async def classement(self, interaction: discord.Interaction):
        """Affiche le classement des utilisateurs avec XP et prestige."""
        await interaction.response.defer(ephemeral=True)

        sorted_xp = sorted(self.xp_data.items(), key=lambda x: (x[1]["prestige"], x[1]["level"], x[1]["xp"]), reverse=True)

        if not sorted_xp:
            await interaction.followup.send("⚠️ Aucun utilisateur avec de l'XP trouvé.", ephemeral=True)
            return

        embed = discord.Embed(title="🏆 **Classement des utilisateurs**", color=discord.Color.gold())

        members = []
        for user_id, data in sorted_xp[:10]:
            member = interaction.guild.get_member(int(user_id))
            if member:
                members.append((member, data))

        for idx, (member, data) in enumerate(members, start=1):
            embed.add_field(
                name=f"{idx}. {member.display_name}",
                value=f"⭐ `Prestige {data['prestige']}` | 🆙 `Niveau {data['level']}` | 📈 `{data['xp']} EXP`",
                inline=False
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="reset_xp", description="Réinitialise l'XP d'un utilisateur.")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_xp(self, interaction: discord.Interaction, member: discord.Member):
        """Réinitialise l'XP d'un utilisateur (Admin uniquement)."""
        await interaction.response.defer(ephemeral=True)

        user_id = str(member.id)
        if user_id in self.xp_data:
            self.xp_data[user_id] = {"xp": 0, "level": 1, "prestige": 0}
            self.save_xp_data()
            await interaction.followup.send(f"✅ XP de {member.mention} réinitialisé avec succès !", ephemeral=True)
        else:
            await interaction.followup.send("⚠️ L'utilisateur n'a pas encore d'XP.", ephemeral=True)

    @app_commands.command(name="progression", description="Montre l'XP restant avant le prochain niveau.")
    async def progression(self, interaction: discord.Interaction, member: discord.Member = None):
        """Affiche combien d'XP est nécessaire pour le niveau suivant."""
        await interaction.response.defer(ephemeral=True)

        member = member or interaction.user
        user_id = str(member.id)
        xp_data = self.get_user_data(user_id)

        current_xp = xp_data["xp"]
        current_level = xp_data["level"]
        level_threshold = current_level * 100  # Exemple : 100 XP * niveau actuel

        xp_remaining = level_threshold - current_xp

        embed = discord.Embed(
            title=f"🚀 Progression de {member.display_name}",
            description=f"Tu as **{current_xp} XP** et es au niveau **{current_level}**.",
            color=discord.Color.green()
        )
        embed.add_field(name="🎯 Objectif", value=f"{level_threshold} XP pour atteindre le niveau {current_level + 1}", inline=False)
        embed.add_field(name="📉 XP Restant", value=f"Encore **{xp_remaining} XP** à gagner !", inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Ajoute automatiquement de l'XP aux utilisateurs lorsqu'ils envoient des messages."""
        if message.author.bot:
            return

        user_id = str(message.author.id)
        user_data = self.get_user_data(user_id)
        user_data["xp"] += 5  # Ajouter 5 XP par message
        
        level_threshold = user_data["level"] * 100
        if user_data["xp"] >= level_threshold:
            user_data["xp"] -= level_threshold
            user_data["level"] += 1
            await message.channel.send(f"🎉 {message.author.mention} est monté au niveau {user_data['level']} !")

        self.save_xp_data()

async def setup(bot: commands.Bot):
    """Ajoute le Cog au bot et force la synchronisation des commandes."""
    cog = ExpCommands(bot)
    await bot.add_cog(cog)
