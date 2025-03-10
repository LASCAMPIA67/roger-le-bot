import discord
from discord.ext import commands
import json
import os
import random
import asyncio
from datetime import datetime, timedelta

class ExpSystem(commands.Cog):
    """Gestion de l'expérience et des niveaux des utilisateurs."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.file_path = "xp_data.json"
        self.xp_data: dict[str, dict[str, int]] = {}  # Stocke les XP et niveaux des utilisateurs
        self.xp_cooldowns: dict[str, float] = {}  # Stocke les timestamps des derniers gains d'XP
        self.lock = asyncio.Lock()  # Pour éviter les conflits d'écriture dans le fichier JSON
        self.load_xp_data()

    def load_xp_data(self) -> None:
        """Charge les données XP depuis un fichier JSON, avec gestion des erreurs."""
        if not os.path.exists(self.file_path):
            self.save_xp_data()  # Créer un fichier vide si inexistant

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = f.read().strip()
                self.xp_data = json.loads(data) if data else {}
        except (json.JSONDecodeError, FileNotFoundError):
            self.xp_data = {}
            self.save_xp_data()

    def save_xp_data(self) -> None:
        """Sauvegarde les données XP dans un fichier JSON de manière sécurisée."""
        async def async_save():
            async with self.lock:
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump(self.xp_data, f, indent=4)

        asyncio.create_task(async_save())

    def calculate_xp_required(self, level: int) -> int:
        """Calcule l'XP requis pour atteindre le niveau suivant."""
        return 50 * (level ** 2)

    def add_xp(self, user_id: str, xp_gained: int) -> bool:
        """Ajoute de l'XP à un utilisateur et vérifie la montée de niveau."""
        user_data = self.xp_data.setdefault(user_id, {"xp": 0, "level": 1})
        user_data["xp"] += xp_gained

        next_level_xp = self.calculate_xp_required(user_data["level"])
        if user_data["xp"] >= next_level_xp:
            user_data["level"] += 1
            user_data["xp"] -= next_level_xp  # Conserve l'XP excédentaire
            self.save_xp_data()
            return True  # Le joueur monte de niveau

        self.save_xp_data()
        return False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Ajoute de l'XP lorsqu'un utilisateur envoie un message, avec anti-spam."""
        if message.author.bot or not message.guild:
            return

        user_id = str(message.author.id)
        now_timestamp = datetime.utcnow().timestamp()

        # Vérification du cooldown d'XP (1 minute entre chaque gain)
        if user_id in self.xp_cooldowns and now_timestamp - self.xp_cooldowns[user_id] < 60:
            return

        self.xp_cooldowns[user_id] = now_timestamp
        xp_gained = random.randint(5, 15)
        leveled_up = self.add_xp(user_id, xp_gained)

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
