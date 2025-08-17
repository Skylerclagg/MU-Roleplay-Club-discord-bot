import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config

class AddUserToChannel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="addusertochannel", description="Add a user to a channel (permission controlled).")
    async def addusertochannel(self, interaction: discord.Interaction, channel: discord.TextChannel, target: discord.Member):
        config = await get_guild_config(interaction.guild)
        user_id = interaction.user.id
        # Permission check: if not admin/mod or developer override.
        if (not interaction.user.guild_permissions.administrator and
            not any(r.id in config.get("mod_roles", []) for r in interaction.user.roles) and 
            interaction.user.id not in [348286042136117251, 123456789012345678]):
            allowed_channels = config.get("command_permissions", {}).get("addusertochannel", {}).get(str(user_id), [])
            if channel.id not in allowed_channels and 0 not in allowed_channels:
                await interaction.response.send_message("You are not authorized to use this command", ephemeral=True)
                return
        try:
            await channel.set_permissions(target, overwrite=discord.PermissionOverwrite(view_channel=True))
            await interaction.response.send_message(f"{target.mention} was added to {channel.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to add user to channel: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AddUserToChannel(bot))
