import discord
from discord.ext import commands
from discord import app_commands

class Creator(commands.Cog):
    """Gestion des salons avec un panneau interactif."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="panel", description="Affiche un panneau interactif pour gérer les salons.")
    async def panel(self, interaction: discord.Interaction):
        """Affiche un panneau pour créer, modifier ou supprimer des salons."""
        view = PanelView()
        embed = discord.Embed(
            title="📌 Panneau de Gestion",
            description="Utilisez les boutons pour gérer les salons.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class PanelView(discord.ui.View):
    """Vue interactive avec des boutons pour gérer les salons."""

    @discord.ui.button(label="Créer un Salon", style=discord.ButtonStyle.success)
    async def create_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Créer un salon textuel."""
        guild = interaction.guild
        new_channel = await guild.create_text_channel("nouveau-salon")
        await interaction.response.send_message(f"✅ Salon {new_channel.mention} créé.", ephemeral=True)

    @discord.ui.button(label="Supprimer un Salon", style=discord.ButtonStyle.danger)
    async def delete_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Supprime le dernier salon créé."""
        guild = interaction.guild
        channels = guild.text_channels
        if channels:
            await channels[-1].delete()
            await interaction.response.send_message(f"🗑️ Salon supprimé.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Aucun salon à supprimer.", ephemeral=True)

    @discord.ui.button(label="Modifier un Salon", style=discord.ButtonStyle.primary)
    async def rename_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Renomme le dernier salon créé."""
        guild = interaction.guild
        channels = guild.text_channels
        if channels:
            await channels[-1].edit(name="salon-modifié")
            await interaction.response.send_message(f"✏️ Salon renommé en **salon-modifié**.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Aucun salon à modifier.", ephemeral=True)

async def setup(bot: commands.Bot):
    """Ajoute le cog Creator au bot."""
    await bot.add_cog(Creator(bot))
