import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config, save_guild_config, parse_time_limit, format_time
from utils.permissions import mod_check

class SetTimeoutLimit(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="settimeoutlimit", description="Set overall verification timeout (e.g., 1d, 1h, 1m, 30s).")
    @app_commands.check(mod_check)
    async def settimeoutlimit(self, interaction: discord.Interaction, time_limit: str):
        seconds = parse_time_limit(time_limit)
        if seconds is None:
            await interaction.response.send_message("Invalid time format. Use formats like 1d, 1h, 1m, or 30s.", ephemeral=True)
            return
        config = await get_guild_config(interaction.guild)
        config["timeout_limit"] = seconds
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(f"Timeout limit set to {format_time(seconds)}.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetTimeoutLimit(bot))
