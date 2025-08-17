import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config, save_guild_config
from utils.permissions import mod_check

class SetPostReminderAction(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setpostreminderaction", description="Set the action after overall reminder timeout (send_dm, continue_wait, kick).")
    @app_commands.check(mod_check)
    async def setpostreminderaction(self, interaction: discord.Interaction, action: str):
        action = action.lower()
        if action not in ["send_dm", "continue_wait", "kick"]:
            await interaction.response.send_message("Invalid action. Options: send_dm, continue_wait, kick.", ephemeral=True)
            return
        config = await get_guild_config(interaction.guild)
        config["post_reminder_action"] = action
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(f"Post-reminder action set to {action}.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetPostReminderAction(bot))
