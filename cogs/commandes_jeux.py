import discord
import random
from discord.ext import commands
from config import logger

class Jeux(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(description="Effectue un calcul simple (+, -, *, /).")
    async def calc(self, ctx: commands.Context, valeur_a: float, operation: str, valeur_b: float):
        if operation == '/' and valeur_b == 0:
            return await ctx.send("⛔ Division par zéro impossible.")
        
        operations = {"+": valeur_a + valeur_b, "-": valeur_a - valeur_b,
                      "*": valeur_a * valeur_b, "/": valeur_a / valeur_b}

        result = operations.get(operation)
        if result is None:
            return await ctx.send("⛔ Opérateur invalide (+, -, *, / uniquement).")

        await ctx.send(f"🧮 `{valeur_a} {operation} {valeur_b}` = `{result}`")
        logger.info(f"Calcul par {ctx.author} : {valeur_a}{operation}{valeur_b} = {result}")

    @commands.hybrid_command(description="Jouer à Pierre-Feuille-Ciseau contre le bot.")
    async def pfc(self, ctx: commands.Context):
        await ctx.send("Choisissez votre coup :", view=PFCView(), ephemeral=True)

class PFCView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.choices = ["pierre", "feuille", "ciseau"]

    async def play_game(self, interaction: discord.Interaction, choix: str):
        bot_choice = random.choice(self.choices)
        conditions = {"pierre": "ciseau", "feuille": "pierre", "ciseau": "feuille"}

        result = ("Égalité 🤝" if choix == bot_choice else
                  "Gagné 🎉" if conditions[choix] == bot_choice else "Perdu 😢")

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(view=self)
        await interaction.followup.send(
            f"🎮 Vous : {choix.capitalize()}\n🤖 Bot : {bot_choice.capitalize()}\n🏆 Résultat : {result}",
            ephemeral=True
        )

    @discord.ui.button(label="Pierre 🪨", style=discord.ButtonStyle.primary)
    async def pierre(self, interaction, button):
        await self.play_game(interaction, "pierre")

    @discord.ui.button(label="Feuille 📄", style=discord.ButtonStyle.primary)
    async def feuille(self, interaction, button):
        await self.play_game(interaction, "feuille")

    @discord.ui.button(label="Ciseau ✂️", style=discord.ButtonStyle.primary)
    async def ciseau(self, interaction, button):
        await self.play_game(interaction, "ciseau")

async def setup(bot: commands.Bot):
    await bot.add_cog(Jeux(bot))
