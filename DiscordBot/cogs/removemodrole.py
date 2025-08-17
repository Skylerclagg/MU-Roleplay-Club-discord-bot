import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config, save_guild_config
from utils.permissions import mod_check

class RemoveModRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="removemodrole", description="Remove a mod role.")
    @app_commands.check(mod_check)
    async def removemodrole(self, interaction: discord.Interaction, role: discord.Role):
        config = await get_guild_config(interaction.guild)
        mod_roles = config.get("mod_roles", [])
        if role.id in mod_roles:
            mod_roles.remove(role.id)
            config["mod_roles"] = mod_roles
            await save_guild_config(interaction.guild, config)
            await interaction.response.send_message(f"Removed mod role: {role.name}", ephemeral=True)
        else:
            await interaction.response.send_message("This role is not in the mod roles list.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(RemoveModRole(bot))
