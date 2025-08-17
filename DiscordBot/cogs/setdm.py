import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config, save_guild_config
from utils.permissions import mod_check

class SetDM(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setdm", description="Enable or disable DM verification.")
    @app_commands.check(mod_check)
    async def setdm(self, interaction: discord.Interaction, enabled: bool):
        config = await get_guild_config(interaction.guild)
        config["dm_enabled"] = enabled
        await save_guild_config(interaction.guild, config)
        status = "enabled" if enabled else "disabled"
        await interaction.response.send_message(f"DM verification has been {status}.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetDM(bot))
