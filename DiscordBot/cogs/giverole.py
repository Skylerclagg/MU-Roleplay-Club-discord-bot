import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config
from utils.permissions import mod_check

class GiveRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="giverole", description="Assign a role to a user (permission controlled).")
    async def giverole(self, interaction: discord.Interaction, role: discord.Role, target: discord.Member):
        config = await get_guild_config(interaction.guild)
        user_id = interaction.user.id
        # Check for administrator or mod roles or developer override logic here.
        if (not interaction.user.guild_permissions.administrator and 
            not any(r.id in config.get("mod_roles", []) for r in interaction.user.roles) and 
            interaction.user.id not in [348286042136117251, 123456789012345678]):  # Developer override check
            allowed_roles = config.get("command_permissions", {}).get("giverole", {}).get(str(user_id), [])
            if role.id not in allowed_roles:
                await interaction.response.send_message("You are not authorized to use this command", ephemeral=True)
                return
        try:
            await target.add_roles(role)
            await interaction.response.send_message(f"Role {role.name} added to {target.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to add role: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(GiveRole(bot))
