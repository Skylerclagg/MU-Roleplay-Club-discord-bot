import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config, save_guild_config
from utils.permissions import mod_check

class SetWelcomeMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setwelcomemessage", description="Set welcome message; use {user} for mention.")
    @app_commands.check(mod_check)
    async def setwelcomemessage(self, interaction: discord.Interaction, message: str):
        # Fetch the guild configuration, update the welcome message and save the configuration.
        config = await get_guild_config(interaction.guild)
        config["welcome_message"] = message
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(f"Welcome message set to:\n{message}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetWelcomeMessage(bot))
