import discord
import locale
from discord import app_commands
from discord.ext import commands

# Configuration de la locale pour le formatage des nombres
locale.setlocale(locale.LC_ALL, '')

class CommandesUtiles(commands.Cog):
    """Commandes utiles du bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Affiche les commandes disponibles et des astuces.")
    async def help(self, interaction: discord.Interaction):
        """Affiche la liste des commandes disponibles et leurs descriptions."""
        embed = discord.Embed(
            title="📜 Liste des commandes disponibles",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="🔧 Utilitaires",
            value=(
                "`/ping` - Voir la latence du bot\n"
                "`/help` - Afficher ce message\n"
                "`/calc` - Calculatrice\n"
                "`/panel` - Panel interactif de gestion des salons (Admin)"
            ),
            inline=False
        )

        embed.add_field(
            name="🛡️ Modération",
            value=(
                "`/kick` - Expulser un membre (Admin)\n"
                "`/ban` - Bannir un membre (Admin)\n"
                "`/deban` - Débannir un membre (Admin)\n"
                "`/clear` - Supprimer des messages (Admin)"
            ),
            inline=False
        )

        embed.add_field(
            name="📊 Expérience",
            value=(
                "`/exp` - Voir sa carte de statistiques\n"
                "`/classement` - Voir le classement\n"
                "`/ajouter_xp` - Ajouter de l'XP (Admin)\n"
                "`/reset_xp` - Réinitialiser l'XP (Admin)\n"
                "`/progression` - Voir sa progression"
            ),
            inline=False
        )

        embed.add_field(
            name="🌐 Réseau",
            value="`/monip` - Voir son IP publique",
            inline=False
        )

        embed.set_footer(text="💡 Astuce : Tapez / suivi du nom d'une commande pour l'exécuter !")

        await interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"📜 Commande /help exécutée par {interaction.user.display_name}")

    @app_commands.command(name="calc", description="Effectue un calcul simple (+, -, *, /).")
    async def calc(self, interaction: discord.Interaction, valeur_a: float, operation: str, valeur_b: float):
        """Effectue un calcul entre deux nombres et affiche le résultat."""
        operations = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b if b != 0 else None  # Vérification de division par zéro
        }

        await interaction.response.defer(ephemeral=True)  # Évite l'erreur d'interaction déjà traitée

        if operation not in operations:
            await interaction.followup.send("⛔ Opérateur invalide ! Utilisez +, -, *, ou /.")
            print(f"❌ Opérateur invalide tenté par {interaction.user.display_name}: {operation}")
            return

        result = operations[operation](valeur_a, valeur_b)
        if result is None:
            await interaction.followup.send("⛔ Division par zéro impossible.")
            print(f"❌ Division par zéro tentée par {interaction.user.display_name}: {valeur_a} / {valeur_b}")
            return

        response = f"🧮 {valeur_a} {operation} {valeur_b} = {locale.format_string('%.2f', result, grouping=True)}"
        await interaction.followup.send(response)
        print(f"🧮 Calcul effectué par {interaction.user.display_name}: {valeur_a} {operation} {valeur_b} = {result}")

async def setup(bot: commands.Bot):
    """Ajoute le cog CommandesUtiles au bot."""
    await bot.add_cog(CommandesUtiles(bot))
