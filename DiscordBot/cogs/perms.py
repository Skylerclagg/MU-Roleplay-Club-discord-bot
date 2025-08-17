import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal
from utils.guild_config import get_guild_config, save_guild_config
from utils.permissions import mod_check

class PermissionsManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="perms", description="Manage permissions for role and channel commands.")
    @app_commands.check(mod_check)
    async def perms(
            self,
            interaction: discord.Interaction,
            action: Literal["allow", "deny"],
            target: discord.Member,
            command: Literal["giverole", "removerole", "addusertochannel", "removeuserfromchannel"],
            role: Optional[discord.Role] = None,
            channel: Optional[discord.TextChannel] = None
        ):
        config = await get_guild_config(interaction.guild)
        perms_config = config.get("command_permissions", {}).get(command, {})
        if command in ["giverole", "removerole"]:
            if role is None:
                await interaction.response.send_message("You must specify a role for this command.", ephemeral=True)
                return
            permission_value = role.id
        else:
            permission_value = channel.id if channel else 0
        user_perms = perms_config.get(str(target.id), [])
        if action == "allow":
            if permission_value not in user_perms:
                user_perms.append(permission_value)
            perms_config[str(target.id)] = user_perms
            config["command_permissions"][command] = perms_config
            await save_guild_config(interaction.guild, config)
            value_display = role.mention if role else (channel.mention if channel else "all channels")
            await interaction.response.send_message(f"Granted permission: {target.mention} can now {command} {value_display}.", ephemeral=True)
        else:
            if permission_value in user_perms:
                user_perms.remove(permission_value)
                perms_config[str(target.id)] = user_perms
                config["command_permissions"][command] = perms_config
                await save_guild_config(interaction.guild, config)
                value_display = role.mention if role else (channel.mention if channel else "all channels")
                await interaction.response.send_message(f"Revoked permission: {target.mention} can no longer {command} {value_display}.", ephemeral=True)
            else:
                await interaction.response.send_message("That permission was not set for the user.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(PermissionsManager(bot))
