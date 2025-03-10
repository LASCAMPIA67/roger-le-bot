import discord
import random
import asyncio
from discord import app_commands
from discord.ext import commands
from config import logger

class Jeux(commands.Cog):
    """Cog contenant des jeux interactifs comme une calculatrice simple et Pierre-Feuille-Ciseau."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="calc", description="Effectue un calcul simple (+, -, *, /).")
    async def calc(self, interaction: discord.Interaction, valeur_a: float, operation: str, valeur_b: float):
        """
        Effectue un calcul entre deux nombres et affiche le résultat.
        Vérifie que l'opérateur est valide et évite la division par zéro.
        """
        operations = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b if b != 0 else None  # Vérification de division par zéro
        }

        if operation not in operations:
            await interaction.response.send_message(
                "⛔ Opérateur invalide ! Utilisez +, -, *, ou /.", ephemeral=True
            )
            return

        result = operations[operation](valeur_a, valeur_b)
        if result is None:
            await interaction.response.send_message(
                "⛔ Division par zéro impossible.", ephemeral=True
            )
            return

        response = f"🧮 {valeur_a} {operation} {valeur_b} = {result}"
        await interaction.response.send_message(response)
        logger.info(f"🧮 Calcul effectué par {interaction.user}: {valeur_a} {operation} {valeur_b} = {result}")

    @app_commands.command(name="pfc", description="Jouer à Pierre-Feuille-Ciseau contre le bot.")
    async def pfc(self, interaction: discord.Interaction):
        """
        Démarre une partie de Pierre-Feuille-Ciseau en affichant un message interactif
        avec des boutons pour choisir son coup.
        """
        view = PFCView()
        # Envoi d'un message avec les boutons interactifs, et le message est éphémère
        await interaction.response.send_message("🎮 **Choisissez votre coup :**", view=view, ephemeral=True)
        logger.info(f"🎮 Jeu Pierre-Feuille-Ciseau lancé par {interaction.user}")

class PFCView(discord.ui.View):
    """Vue interactive pour le jeu Pierre-Feuille-Ciseau."""

    def __init__(self):
        super().__init__(timeout=30)  # Timeout pour désactiver les boutons après 30 secondes
        self.choices = ["pierre", "feuille", "ciseau"]

    async def on_timeout(self):
        """Désactive tous les boutons si aucun choix n'est effectué avant le timeout."""
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    async def play_game(self, interaction: discord.Interaction, choix: str):
        """
        Traite le choix de l'utilisateur, calcule le résultat contre le bot et renvoie
        une réponse éphémère. Après l'interaction, on efface le message et force l'utilisateur
        à refaire la commande.
        """
        await interaction.response.defer()  # Indique que le traitement est en cours
        bot_choice = random.choice(self.choices)
        conditions = {"pierre": "ciseau", "feuille": "pierre", "ciseau": "feuille"}

        if choix == bot_choice:
            result = "Égalité 🤝"
        elif conditions[choix] == bot_choice:
            result = "Gagné 🎉"
        else:
            result = "Perdu 😢"

        # Désactiver les boutons pour éviter d'autres interactions
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

        # Tenter d'éditer le message original pour désactiver les boutons
        try:
            await interaction.message.edit(view=self)
        except Exception:
            pass

        # Créer un message combiné pour afficher le résultat du jeu et inviter l'utilisateur à refaire la commande
        message = (
            f"🎮 **Vous :** {choix.capitalize()}\n"
            f"🤖 **Bot :** {bot_choice.capitalize()}\n"
            f"🏆 **Résultat :** {result}\n"
            f"🔁 **Le jeu est terminé, refaites la commande `/pfc` pour jouer à nouveau.**"
        )

        # Envoi du résultat via une réponse de suivi éphémère
        await interaction.followup.send(
            message,
            ephemeral=True
        )
        logger.info(f"🎮 PFC - {interaction.user} a joué {choix}, le bot a joué {bot_choice}. Résultat : {result}")

        # Effacer le message de la commande
        try:
            await interaction.delete_original_response()
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du message original: {e}")

    @discord.ui.button(label="Pierre 🪨", style=discord.ButtonStyle.primary)
    async def pierre(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton permettant de choisir Pierre."""
        await self.play_game(interaction, "pierre")

    @discord.ui.button(label="Feuille 📄", style=discord.ButtonStyle.primary)
    async def feuille(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton permettant de choisir Feuille."""
        await self.play_game(interaction, "feuille")

    @discord.ui.button(label="Ciseau ✂️", style=discord.ButtonStyle.primary)
    async def ciseau(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton permettant de choisir Ciseau."""
        await self.play_game(interaction, "ciseau")

async def setup(bot: commands.Bot):
    """Ajoute le Cog 'Jeux' au bot."""
    await bot.add_cog(Jeux(bot))
