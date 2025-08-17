import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config, format_time
from utils.permissions import mod_check

class ConfigStatus(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="configstatus", description="Show current server configuration settings.")
    @app_commands.check(mod_check)
    async def configstatus(self, interaction: discord.Interaction):
        config = await get_guild_config(interaction.guild)
        guild = interaction.guild

        # Format welcome channel display
        welcome_channel_id = config.get("welcome_channel")
        if welcome_channel_id:
            channel_obj = guild.get_channel(welcome_channel_id)
            welcome_channel_str = channel_obj.mention if channel_obj else str(welcome_channel_id)
        else:
            welcome_channel_str = "Not set"

        # Format role given display
        role_given_id = config.get("role_given")
        if role_given_id:
            role_obj = guild.get_role(role_given_id)
            role_given_str = role_obj.mention if role_obj else str(role_given_id)
        else:
            role_given_str = "Not set"

        # DM status
        dm_enabled = config.get("dm_enabled", False)
        dm_status = "Enabled" if dm_enabled else "Disabled"

        # Build permissions string (for a few commands; adjust as needed)
        command_permissions = config.get("command_permissions", {})
        perms_str = ""
        for cmd in ["giverole", "removerole", "addusertochannel", "removeuserfromchannel"]:
            perms = command_permissions.get(cmd, {})
            if perms:
                perms_str += f"**{cmd}:**\n"
                for user_id, allowed in perms.items():
                    member_obj = guild.get_member(int(user_id))
                    member_str = member_obj.mention if member_obj else user_id
                    if isinstance(allowed, list):
                        allowed_strs = []
                        for id_val in allowed:
                            if id_val == 0:
                                allowed_strs.append("all")
                            else:
                                if cmd in ["giverole", "removerole"]:
                                    r = guild.get_role(id_val)
                                    allowed_strs.append(r.name if r else str(id_val))
                                else:
                                    c = guild.get_channel(id_val)
                                    allowed_strs.append(c.mention if c else str(id_val))
                        perms_str += f"  {member_str}: {', '.join(allowed_strs)}\n"
                    else:
                        perms_str += f"  {member_str}: {allowed}\n"
            else:
                perms_str += f"**{cmd}:** None\n"

        config_text = (
            f"**Server Configuration:**\n"
            f"**Welcome Message:** {config.get('welcome_message', 'Not set')}\n"
            f"**Welcome Channel:** {welcome_channel_str}\n"
            f"**Role Given:** {role_given_str}\n"
            f"**DM Verification:** {dm_status}\n"
            f"**DM Welcome Message:** {config.get('dm_welcome_message', 'Not set')}\n"
            f"**Reminder Message:** {config.get('reminder_message', 'Not set')}\n"
            f"**Timeout Action:** {config.get('timeout_action', 'remind')}\n"
            f"**Timeout Limit:** {format_time(config.get('timeout_limit', 86400))}\n"
            f"**Reminder Interval:** {format_time(config.get('reminder_interval', 3600))}\n"
            f"**Overall Reminder Timeout:** {format_time(config.get('reminder_timeout', 86400))}\n"
            f"**Post-Reminder Action:** {config.get('post_reminder_action', 'continue_wait')}\n"
            f"**Post-Reminder Message:** {config.get('post_reminder_message', 'Not set')}\n"
            f"**Mod Roles:** {', '.join([guild.get_role(r).name if guild.get_role(r) else str(r) for r in config.get('mod_roles', [])]) or 'None'}\n"
            f"**Command Permissions:**\n{perms_str}"
        )

        await interaction.response.send_message(config_text, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ConfigStatus(bot))
