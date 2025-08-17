import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config, save_guild_config

class AddModRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="addmodrole", description="Add a mod role.")
    async def addmodrole(self, interaction: discord.Interaction, role: discord.Role):
        # Retrieve configuration for the guild
        config = await get_guild_config(interaction.guild)
        mod_roles = config.get("mod_roles", [])
        # Add the role to the mod roles list if it's not already present
        if role.id not in mod_roles:
            mod_roles.append(role.id)
        config["mod_roles"] = mod_roles
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(f"Added mod role: {role.name}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AddModRole(bot))
