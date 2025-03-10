import discord
from discord.ext import commands
import json
import os
import random
from datetime import datetime, timedelta

class ExpSystem(commands.Cog):
    """Gestion de l'expérience et des niveaux des utilisateurs."""

    def __init__(self, bot):
        self.bot = bot
        self.file_path = "xp_data.json"
        self.load_xp_data()
        self.xp_cooldowns = {}  # Stocke les derniers gains d'XP pour éviter le spam

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

    def calculate_xp_required(self, level: int) -> int:
        """Calcule l'XP requis pour atteindre le niveau suivant."""
        return 50 * (level ** 2)

    def add_xp(self, user_id: str, xp_gained: int):
        """Ajoute de l'XP à un utilisateur et vérifie la montée de niveau."""
        if user_id not in self.xp_data:
            self.xp_data[user_id] = {"xp": 0, "level": 1}

        self.xp_data[user_id]["xp"] += xp_gained
        current_level = self.xp_data[user_id]["level"]
        next_level_xp = self.calculate_xp_required(current_level)

        if self.xp_data[user_id]["xp"] >= next_level_xp:
            self.xp_data[user_id]["level"] += 1
            self.xp_data[user_id]["xp"] -= next_level_xp  # Conserve l'XP excédentaire
            self.save_xp_data()
            return True  # Le joueur monte de niveau

        self.save_xp_data()
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        """Ajoute de l'XP lorsqu'un utilisateur envoie un message, avec anti-spam."""
        if message.author.bot:
            return

        user_id = str(message.author.id)
        now = datetime.utcnow()

        # Vérification du cooldown d'XP (1 minute entre chaque gain)
        if user_id in self.xp_cooldowns:
            last_xp_time = self.xp_cooldowns[user_id]
            if now - last_xp_time < timedelta(seconds=60):
                return

        self.xp_cooldowns[user_id] = now
        xp_gained = random.randint(5, 15)
        leveled_up = self.add_xp(user_id, xp_gained)

        if leveled_up:
            await message.channel.send(f"🎉 {message.author.mention} a atteint le niveau **{self.xp_data[user_id]['level']}** !")

async def setup(bot):
    """Ajoute le cog ExpSystem au bot."""
    await bot.add_cog(ExpSystem(bot))
