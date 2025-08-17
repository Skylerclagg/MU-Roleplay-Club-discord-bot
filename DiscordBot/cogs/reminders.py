import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal
from utils.guild_config import get_guild_config, save_guild_config
from utils.permissions import mod_check

class Reminders(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="reminders", description="Enable or disable verification reminders.")
    @app_commands.describe(option="Choose to enable or disable reminders")
    @app_commands.check(mod_check)
    async def reminders(self, interaction: discord.Interaction, option: Literal["enable", "disable"]):
        # Retrieve the guild's configuration.
        config = await get_guild_config(interaction.guild)
        
        # Update the configuration depending on the option.
        if option == "enable":
            config["reminders_enabled"] = True
            response = "Verification reminders have been enabled for this server."
        else:
            config["reminders_enabled"] = False
            response = "Verification reminders have been disabled for this server."
        
        # Save the updated configuration.
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(response, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Reminders(bot))
