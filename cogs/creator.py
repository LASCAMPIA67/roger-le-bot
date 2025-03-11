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
        if not interaction.guild:
            await interaction.response.send_message("❌ Cette commande doit être utilisée dans un serveur.", ephemeral=True)
            return

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

        if not guild:
            await interaction.response.send_message("❌ Impossible d'exécuter cette action en message privé.", ephemeral=True)
            return

        if not guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Je n'ai pas la permission de créer des salons.", ephemeral=True)
            return

        new_channel = await guild.create_text_channel("nouveau-salon")
        await interaction.response.send_message(f"✅ Salon {new_channel.mention} créé.", ephemeral=True)
        print(f"✅ Salon {new_channel.name} créé par {interaction.user.display_name}")

    @discord.ui.button(label="Supprimer un Salon", style=discord.ButtonStyle.danger)
    async def delete_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Supprime le dernier salon créé."""
        guild = interaction.guild

        if not guild:
            await interaction.response.send_message("❌ Impossible d'exécuter cette action en message privé.", ephemeral=True)
            return

        if not guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Je n'ai pas la permission de supprimer des salons.", ephemeral=True)
            return

        channels = [c for c in guild.text_channels if c.permissions_for(guild.me).manage_channels]
        if channels:
            last_channel = channels[-1]
            await last_channel.delete()
            await interaction.response.send_message(f"🗑️ Salon **{last_channel.name}** supprimé.", ephemeral=True)
            print(f"🗑️ Salon {last_channel.name} supprimé par {interaction.user.display_name}")
        else:
            await interaction.response.send_message("⚠️ Aucun salon à supprimer.", ephemeral=True)

    @discord.ui.button(label="Modifier un Salon", style=discord.ButtonStyle.primary)
    async def rename_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Renomme le dernier salon créé."""
        guild = interaction.guild

        if not guild:
            await interaction.response.send_message("❌ Impossible d'exécuter cette action en message privé.", ephemeral=True)
            return

        if not guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Je n'ai pas la permission de modifier des salons.", ephemeral=True)
            return

        channels = [c for c in guild.text_channels if c.permissions_for(guild.me).manage_channels]
        if channels:
            last_channel = channels[-1]
            old_name = last_channel.name
            await last_channel.edit(name="salon-modifié")
            await interaction.response.send_message(f"✏️ Salon **{old_name}** renommé en **salon-modifié**.", ephemeral=True)
            print(f"✏️ Salon {old_name} renommé en 'salon-modifié' par {interaction.user.display_name}")
        else:
            await interaction.response.send_message("⚠️ Aucun salon à modifier.", ephemeral=True)

async def setup(bot: commands.Bot):
    """Ajoute le cog Creator au bot."""
    await bot.add_cog(Creator(bot))
