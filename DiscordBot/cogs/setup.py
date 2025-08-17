import discord
from discord import app_commands
from discord.ext import commands

from utils.permissions import mod_check
from views.setup_view import MainSetupView # Import our new view

class SetupCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Open the interactive setup panel for the bot.")
    @app_commands.check(mod_check)
    async def setup(self, interaction: discord.Interaction):
        """Launches the main setup view."""
        # The view will handle all the logic from here
        view = MainSetupView(interaction)
        embed = discord.Embed(
            title="👋 Welcome Bot Setup Panel",
            description="Select a category below to begin configuring the bot for your server.",
            color=discord.Color.purple()
        )
        embed.set_footer(text="This panel will time out after 3 minutes of inactivity.")
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetupCog(bot))
