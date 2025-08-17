import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from utils.guild_config import get_guild_config, save_guild_config
from utils.permissions import mod_check

class ConfirmationConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="setconfirmation",
        description="Configure the verification confirmation message settings."
    )
    @app_commands.describe(
        enabled="Set to true to enable a confirmation message after verification, false to disable.",
        message="The confirmation message text (use {user} as a placeholder for user mention).",
        dm="Set to true to send the confirmation message via DM; false to send it in the welcome channel (if available)."
    )
    @app_commands.check(mod_check)
    async def setconfirmation(
        self,
        interaction: discord.Interaction,
        enabled: bool,
        message: str,
        dm: bool
    ):
        # Get the current guild configuration.
        config = await get_guild_config(interaction.guild)
        # Update configuration with the new confirmation settings.
        config["verification_confirmation_enabled"] = enabled
        config["verification_confirmation_message"] = message
        config["verification_confirmation_dm"] = dm
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(
            "Verification confirmation settings updated.",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(ConfirmationConfig(bot))
