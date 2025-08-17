import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config
from utils.permissions import mod_check

class ListModRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="listmodroles", description="List mod roles.")
    @app_commands.check(mod_check)
    async def listmodroles(self, interaction: discord.Interaction):
        config = await get_guild_config(interaction.guild)
        mod_roles = config.get("mod_roles", [])
        if not mod_roles:
            await interaction.response.send_message("No mod roles have been set.", ephemeral=True)
        else:
            role_names = []
            for role_id in mod_roles:
                role = interaction.guild.get_role(role_id)
                if role:
                    role_names.append(role.name)
                else:
                    role_names.append(str(role_id))
            roles_str = ", ".join(role_names)
            await interaction.response.send_message(f"Mod roles: {roles_str}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ListModRoles(bot))
