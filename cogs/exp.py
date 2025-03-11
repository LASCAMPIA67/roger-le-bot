import discord
from discord.ext import commands
import json
import os
import random
import asyncio
from datetime import datetime

class ExpSystem(commands.Cog):
    """Gestion de l'expérience, des niveaux et des prestiges des utilisateurs."""

    XP_PER_LEVEL_BASE = 100  # XP de base nécessaire pour monter en niveau
    LEVEL_CAP = 100  # Niveau maximal avant prestige
    PRESTIGE_BONUS = 1.3  # Augmentation exponentielle de l'XP requise par prestige
    XP_COOLDOWN = 60  # Délai en secondes entre chaque gain d'XP

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.file_path = "xp_data.json"
        self.xp_data = {}
        self.xp_cooldowns = {}
        self.lock = asyncio.Lock()
        self.load_xp_data()

    def load_xp_data(self) -> None:
        """Charge les données d'XP depuis un fichier JSON."""
        if not os.path.exists(self.file_path):
            self.save_xp_data()

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.xp_data = json.load(f) or {}
        except (json.JSONDecodeError, FileNotFoundError):
            self.xp_data = {}
            self.save_xp_data()

    async def save_xp_data(self) -> None:
        """Sauvegarde les données XP de manière sécurisée."""
        async with self.lock:
            try:
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump(self.xp_data, f, indent=4)
            except Exception as e:
                print(f"⚠️ Erreur lors de la sauvegarde des données XP: {e}")

    def calculate_xp_required(self, level: int, prestige: int) -> int:
        """Calcule l'XP requise pour monter de niveau en tenant compte du prestige."""
        return int(self.XP_PER_LEVEL_BASE * (level ** 1.5) * (self.PRESTIGE_BONUS ** prestige))

    async def add_xp(self, user_id: str, xp_gained: int) -> bool:
        """Ajoute de l'XP à un utilisateur et gère les niveaux et prestiges."""
        user_data = self.xp_data.setdefault(user_id, {"xp": 0, "level": 1, "prestige": 0})
        user_data["xp"] += xp_gained

        leveled_up = False

        while user_data["xp"] >= self.calculate_xp_required(user_data["level"], user_data["prestige"]):
            if user_data["level"] < self.LEVEL_CAP:
                user_data["xp"] -= self.calculate_xp_required(user_data["level"], user_data["prestige"])
                user_data["level"] += 1
                leveled_up = True
            else:
                user_data["xp"] = 0
                user_data["level"] = 1
                user_data["prestige"] += 1
                leveled_up = True

        await self.save_xp_data()
        return leveled_up

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Ajoute de l'XP lors d'un message, avec anti-spam."""
        if message.author.bot or not message.guild:
            return

        user_id = str(message.author.id)
        now = datetime.utcnow().timestamp()

        if user_id in self.xp_cooldowns and now - self.xp_cooldowns[user_id] < self.XP_COOLDOWN:
            return

        self.xp_cooldowns[user_id] = now
        xp_gained = random.randint(5, 15)
        leveled_up = await self.add_xp(user_id, xp_gained)

        if leveled_up:
            embed = discord.Embed(
                title="🎉 Niveau supérieur !",
                description=f"Félicitations {message.author.mention}, tu es maintenant **niveau {self.xp_data[user_id]['level']}** !",
                color=discord.Color.gold()
            )
            await message.channel.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
    """Ajoute le cog ExpSystem au bot."""
    await bot.add_cog(ExpSystem(bot))
