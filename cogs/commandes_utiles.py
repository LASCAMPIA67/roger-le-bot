import discord
from discord import app_commands
from discord.ext import commands

class CommandesUtiles(commands.Cog):
    """Commandes utiles du bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Affiche les commandes disponibles et des astuces.")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 Liste des commandes",
            description="Voici la liste des commandes disponibles :",
            color=discord.Color.blue()
        )

        embed.add_field(name="🔧 Utilitaires", value="/ping - Voir la latence du bot\n/help - Afficher ce message\n/calc - Calculatrice", inline=False)
        embed.add_field(name="🛡️ Modération", value="/kick - Expulser un membre (Admin)\n/ban - Bannir un membre (Admin)\n/deban - Débannir un membre (Admin)\n/clear - Supprimer des blocs de messages (Admin)", inline=False)
        embed.add_field(name="📊 Expérience", value="/exp - Voir son XP\n/classement - Voir le classement\n/ajouter_xp - Ajoute de l'XP à un utilisateur (Admin)", inline=False)
        embed.add_field(name="🌐 Réseau", value="/monip - Voir son IP publique", inline=False)

        embed.set_footer(text="Astuce : Tapez / devant une commande pour l'exécuter !")

        await interaction.response.send_message(embed=embed, ephemeral=True)

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
        await interaction.response.send_message(response, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(CommandesUtiles(bot))
