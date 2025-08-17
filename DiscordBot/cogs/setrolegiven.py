import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config, save_guild_config
from utils.permissions import mod_check

class SetRoleGiven(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setrolegiven", description="Set role to assign to new users.")
    @app_commands.check(mod_check)
    async def setrolegiven(self, interaction: discord.Interaction, role: discord.Role):
        config = await get_guild_config(interaction.guild)
        config["role_given"] = role.id
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(f"Verification role set to: {role.name}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetRoleGiven(bot))
