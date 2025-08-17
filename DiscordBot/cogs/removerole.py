import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config

class RemoveRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="removerole", description="Remove a role from a user (permission controlled).")
    async def removerole(self, interaction: discord.Interaction, role: discord.Role, target: discord.Member):
        config = await get_guild_config(interaction.guild)
        user_id = interaction.user.id
        # Permission check: if not admin/mod or developer override.
        if (not interaction.user.guild_permissions.administrator and 
            not any(r.id in config.get("mod_roles", []) for r in interaction.user.roles) and 
            interaction.user.id not in [348286042136117251, 123456789012345678]):
            allowed_roles = config.get("command_permissions", {}).get("removerole", {}).get(str(user_id), [])
            if role.id not in allowed_roles:
                await interaction.response.send_message("You are not authorized to use this command", ephemeral=True)
                return
        try:
            await target.remove_roles(role)
            await interaction.response.send_message(f"Role **{role.name}** removed from {target.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to remove role: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(RemoveRole(bot))
