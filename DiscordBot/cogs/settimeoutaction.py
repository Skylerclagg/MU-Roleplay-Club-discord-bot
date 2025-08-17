import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config, save_guild_config
from utils.permissions import mod_check

class SetTimeoutAction(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="settimeoutaction", description="Set action on verification timeout (kick, restrict, or remind).")
    @app_commands.check(mod_check)
    async def settimeoutaction(self, interaction: discord.Interaction, action: str):
        # Validate input
        if action.lower() not in ["kick", "restrict", "remind"]:
            await interaction.response.send_message("Invalid action. Options: kick, restrict, remind.", ephemeral=True)
            return
        config = await get_guild_config(interaction.guild)
        config["timeout_action"] = action.lower()
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(f"Timeout action set to **{action.lower()}**.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetTimeoutAction(bot))
