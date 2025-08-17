import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config, save_guild_config
from utils.permissions import mod_check

class SetPostReminderMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setpostremindermessage", description="Set the post-reminder message (used if post_reminder_action is send_dm or kick).")
    @app_commands.check(mod_check)
    async def setpostremindermessage(self, interaction: discord.Interaction, message: str):
        config = await get_guild_config(interaction.guild)
        config["post_reminder_message"] = message
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(f"Post-reminder message set to:\n{message}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetPostReminderMessage(bot))
