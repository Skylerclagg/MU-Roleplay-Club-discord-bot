import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config, save_guild_config, parse_time_limit, format_time
from utils.permissions import mod_check

class SetReminderTimeout(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setremindertimeout", description="Set overall reminder timeout (e.g., 1d, 2d).")
    @app_commands.check(mod_check)
    async def setremindertimeout(self, interaction: discord.Interaction, time_str: str):
        seconds = parse_time_limit(time_str)
        if seconds is None:
            await interaction.response.send_message("Invalid time format. Use a format like '1d' or '2d'.", ephemeral=True)
            return
        config = await get_guild_config(interaction.guild)
        config["reminder_timeout"] = seconds
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(f"Overall reminder timeout set to {format_time(seconds)}.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetReminderTimeout(bot))
