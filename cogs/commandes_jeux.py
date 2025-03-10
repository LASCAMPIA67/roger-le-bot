import discord
import random
from discord import app_commands
from discord.ext import commands
from config import logger

class Jeux(commands.Cog):
    """Cog contenant des jeux interactifs comme une calculatrice simple et Pierre-Feuille-Ciseau."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="calc", description="Effectue un calcul simple (+, -, *, /).")
    async def calc(self, interaction: discord.Interaction, valeur_a: float, operation: str, valeur_b: float):
        """Effectue un calcul entre deux nombres et affiche le résultat."""
        operations = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b if b != 0 else None  # Vérification de division par zéro
        }

        if operation not in operations:
            await interaction.response.send_message(
                "⛔ Opérateur invalide ! Utilisez `+`, `-`, `*`, ou `/`.", ephemeral=True
            )
            return

        result = operations[operation](valeur_a, valeur_b)
        if result is None:
            await interaction.response.send_message(
                "⛔ Division par zéro impossible.", ephemeral=True
            )
            return

        response = f"🧮 `{valeur_a} {operation} {valeur_b}` = `{result}`"
        await interaction.response.send_message(response)
        logger.info(f"🧮 Calcul effectué par {interaction.user}: {valeur_a} {operation} {valeur_b} = {result}")

    @app_commands.command(name="pfc", description="Jouer à Pierre-Feuille-Ciseau contre le bot.")
    async def pfc(self, interaction: discord.Interaction):
        """Démarre une partie de Pierre-Feuille-Ciseau en interaction avec l'utilisateur."""
        view = PFCView()
        await interaction.response.send_message("🎮 **Choisissez votre coup :**", view=view)
        logger.info(f"🎮 Jeu Pierre-Feuille-Ciseau lancé par {interaction.user}")

class PFCView(discord.ui.View):
    """Vue interactive pour le jeu Pierre-Feuille-Ciseau."""

    def __init__(self):
        super().__init__(timeout=30)  # Timeout pour éviter que les boutons restent actifs indéfiniment
        self.choices = ["pierre", "feuille", "ciseau"]

    async def on_timeout(self):
        """Désactive les boutons si aucun choix n'est fait avant le timeout."""
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        # Ici, 'interaction.message' n'est pas directement accessible,
        # il est conseillé de stocker la référence du message lors de l'envoi si nécessaire.

    async def play_game(self, interaction: discord.Interaction, choix: str):
        """Gère une manche de Pierre-Feuille-Ciseau."""
        await interaction.response.defer()  # Indique que le traitement est en cours
        bot_choice = random.choice(self.choices)
        conditions = {"pierre": "ciseau", "feuille": "pierre", "ciseau": "feuille"}

        if choix == bot_choice:
            result = "Égalité 🤝"
        elif conditions[choix] == bot_choice:
            result = "Gagné 🎉"
        else:
            result = "Perdu 😢"

        # Désactiver les boutons après le choix
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

        # Mise à jour de l'affichage du message original si besoin (à adapter selon l'implémentation)
        try:
            await interaction.message.edit(view=self)
        except Exception:
            pass  # Si l'édition échoue, on ne bloque pas l'envoi du résultat

        # Envoi du résultat en réponse
        await interaction.followup.send(
            f"🎮 **Vous :** {choix.capitalize()}\n🤖 **Bot :** {bot_choice.capitalize()}\n🏆 **Résultat :** {result}",
            ephemeral=True
        )
        logger.info(f"🎮 PFC - {interaction.user} a joué {choix}, le bot a joué {bot_choice}. Résultat : {result}")

    @discord.ui.button(label="Pierre 🪨", style=discord.ButtonStyle.primary)
    async def pierre(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour choisir Pierre."""
        await self.play_game(interaction, "pierre")

    @discord.ui.button(label="Feuille 📄", style=discord.ButtonStyle.primary)
    async def feuille(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour choisir Feuille."""
        await self.play_game(interaction, "feuille")

    @discord.ui.button(label="Ciseau ✂️", style=discord.ButtonStyle.primary)
    async def ciseau(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour choisir Ciseau."""
        await self.play_game(interaction, "ciseau")

async def setup(bot: commands.Bot):
    """Ajoute le Cog 'Jeux' au bot."""
    await bot.add_cog(Jeux(bot))
