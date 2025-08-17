import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config, save_guild_config, parse_time_limit, format_time
from utils.permissions import mod_check

class SetReminderInterval(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setreminderinterval", description="Set reminder interval (e.g., 1d, 1h, 1m, 30s).")
    @app_commands.check(mod_check)
    async def setreminderinterval(self, interaction: discord.Interaction, interval: str):
        seconds = parse_time_limit(interval)
        if seconds is None:
            await interaction.response.send_message("Invalid time format. Use formats like 1d, 1h, 1m, or 30s.", ephemeral=True)
            return
        config = await get_guild_config(interaction.guild)
        config["reminder_interval"] = seconds
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(f"Reminder interval set to {format_time(seconds)}.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetReminderInterval(bot))
