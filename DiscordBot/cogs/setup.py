import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal, Optional
from utils.guild_config import get_guild_config, save_guild_config, parse_time_limit, format_time
from utils.permissions import mod_check

class SetupCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Parent group for all setup commands
    setup = app_commands.Group(name="setup", description="Configure the bot for this server.", guild_only=True)

    # --- Message Subcommands ---
    @setup.command(name="message", description="Set the various messages the bot uses.")
    @app_commands.describe(
        type="The type of message you want to set.",
        message="The message content. Use {user} and {server} as placeholders."
    )
    @app_commands.check(mod_check)
    async def setup_message(self, interaction: discord.Interaction, type: Literal["welcome", "dm", "reminder", "post-reminder", "confirmation"], message: str):
        config = await get_guild_config(interaction.guild)
        key_map = {
            "welcome": "welcome_message",
            "dm": "dm_welcome_message",
            "reminder": "reminder_message",
            "post-reminder": "post_reminder_message",
            "confirmation": "verification_confirmation_message"
        }
        key = key_map[type]
        config[key] = message
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(f"✅ The **{type} message** has been set.", ephemeral=True)

    # --- Channel Subcommands ---
    @setup.command(name="channel", description="Set the channels for welcome messages and logs.")
    @app_commands.describe(
        type="The type of channel to set.",
        channel="The text channel to use."
    )
    @app_commands.check(mod_check)
    async def setup_channel(self, interaction: discord.Interaction, type: Literal["welcome", "log"], channel: discord.TextChannel):
        config = await get_guild_config(interaction.guild)
        key = "welcome_channel" if type == "welcome" else "log_channel"
        config[key] = channel.id
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(f"✅ The **{type} channel** has been set to {channel.mention}.", ephemeral=True)

    # --- Role Subcommands ---
    role_group = app_commands.Group(name="role", parent=setup, description="Manage verified and moderator roles.")

    @role_group.command(name="verified", description="Set the role to be given to members after they verify.")
    @app_commands.check(mod_check)
    async def setup_role_verified(self, interaction: discord.Interaction, role: discord.Role):
        config = await get_guild_config(interaction.guild)
        config["role_given"] = role.id
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(f"✅ The verified role has been set to **{role.name}**.", ephemeral=True)

    @role_group.command(name="add-mod", description="Add a role that can use the bot's admin commands.")
    @app_commands.check(mod_check)
    async def setup_role_add_mod(self, interaction: discord.Interaction, role: discord.Role):
        config = await get_guild_config(interaction.guild)
        mod_roles = config.get("mod_roles", [])
        if role.id not in mod_roles:
            mod_roles.append(role.id)
            config["mod_roles"] = mod_roles
            await save_guild_config(interaction.guild, config)
            await interaction.response.send_message(f"✅ **{role.name}** has been added as a mod role.", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ **{role.name}** is already a mod role.", ephemeral=True)

    @role_group.command(name="remove-mod", description="Remove a moderator role.")
    @app_commands.check(mod_check)
    async def setup_role_remove_mod(self, interaction: discord.Interaction, role: discord.Role):
        config = await get_guild_config(interaction.guild)
        mod_roles = config.get("mod_roles", [])
        if role.id in mod_roles:
            mod_roles.remove(role.id)
            config["mod_roles"] = mod_roles
            await save_guild_config(interaction.guild, config)
            await interaction.response.send_message(f"✅ **{role.name}** has been removed from mod roles.", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ **{role.name}** is not a mod role.", ephemeral=True)

    @role_group.command(name="list-mods", description="List the current moderator roles.")
    @app_commands.check(mod_check)
    async def setup_role_list_mods(self, interaction: discord.Interaction):
        config = await get_guild_config(interaction.guild)
        mod_roles = config.get("mod_roles", [])
        if not mod_roles:
            await interaction.response.send_message("No mod roles have been set.", ephemeral=True)
            return
        
        lines = []
        for role_id in mod_roles:
            role = interaction.guild.get_role(role_id)
            lines.append(f"- {role.mention if role else f'`{role_id}` (Deleted Role)'}")
        
        await interaction.response.send_message(f"**Current Mod Roles:**\n" + "\n".join(lines), ephemeral=True)

    # --- Toggle Subcommands ---
    @setup.command(name="toggle", description="Enable or disable features like DM verification.")
    @app_commands.describe(
        feature="The feature to enable or disable.",
        enabled="Set to True to enable, or False to disable."
    )
    @app_commands.check(mod_check)
    async def setup_toggle(self, interaction: discord.Interaction, feature: Literal["dm-verification", "reminders", "confirmation-message"], enabled: bool):
        config = await get_guild_config(interaction.guild)
        key_map = {
            "dm-verification": "dm_enabled",
            "reminders": "reminders_enabled",
            "confirmation-message": "verification_confirmation_enabled"
        }
        key = key_map[feature]
        config[key] = enabled
        await save_guild_config(interaction.guild, config)
        status = "enabled" if enabled else "disabled"
        await interaction.response.send_message(f"✅ **{feature.replace('-', ' ').title()}** has been {status}.", ephemeral=True)

    # --- Verification Subcommands ---
    verification_group = app_commands.Group(name="verification", parent=setup, description="Configure the member verification process.")

    @verification_group.command(name="timeout", description="Set the various timeout durations for verification.")
    @app_commands.describe(
        type="The type of timeout to configure.",
        duration="The duration (e.g., '1d', '8h', '30m', '60s')."
    )
    @app_commands.check(mod_check)
    async def setup_verification_timeout(self, interaction: discord.Interaction, type: Literal["limit", "reminder-interval", "overall-timeout"], duration: str):
        seconds = parse_time_limit(duration)
        if seconds is None:
            await interaction.response.send_message("Invalid time format. Use formats like `1d`, `1h`, `1m`, or `30s`.", ephemeral=True)
            return
        
        config = await get_guild_config(interaction.guild)
        key_map = {
            "limit": "timeout_limit",
            "reminder-interval": "reminder_interval",
            "overall-timeout": "reminder_timeout"
        }
        key = key_map[type]
        config[key] = seconds
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(f"✅ Verification **{type.replace('-', ' ')}** set to **{format_time(seconds)}**.", ephemeral=True)

    @verification_group.command(name="action", description="Set the action to take when a timeout is reached.")
    @app_commands.describe(type="When the action should occur.", action="The action to take.")
    @app_commands.check(mod_check)
    async def setup_verification_action(self, interaction: discord.Interaction, type: Literal['on-timeout', 'post-reminder'], action: str):
        if type == 'on-timeout':
            key = "timeout_action"
            options = ["kick", "restrict", "remind"]
        else: # post-reminder
            key = "post_reminder_action"
            options = ["send_dm", "continue_wait", "kick"]

        if action.lower() not in options:
            await interaction.response.send_message(f"Invalid action. Options are: `{', '.join(options)}`.", ephemeral=True)
            return

        config = await get_guild_config(interaction.guild)
        config[key] = action.lower()
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(f"✅ The **{type.replace('-', ' ')}** action has been set to `{action.lower()}`.", ephemeral=True)
        
    @verification_group.command(name="confirmation", description="Configure the confirmation message sent after successful verification.")
    @app_commands.describe(
        send_in_dm="Set to True to send the confirmation in a DM, False for the welcome channel."
    )
    @app_commands.check(mod_check)
    async def setup_verification_confirmation(self, interaction: discord.Interaction, send_in_dm: bool):
        config = await get_guild_config(interaction.guild)
        config["verification_confirmation_dm"] = send_in_dm
        await save_guild_config(interaction.guild, config)
        location = "user's DMs" if send_in_dm else "the welcome channel"
        await interaction.response.send_message(f"✅ Confirmation messages will now be sent to the **{location}**.", ephemeral=True)
    
    # --- Reset Command ---
    @setup.command(name="reset", description="Reset the server's configuration to the default settings.")
    @app_commands.check(mod_check)
    async def setup_reset(self, interaction: discord.Interaction):
        # Create a default config dictionary
        default_config = {
            "welcome_message": "Welcome {user}! Please reply with your full name to verify.",
            "dm_enabled": False,
            "dm_welcome_message": "Hello {user}, welcome! Please reply with your full name to verify.",
            "welcome_channel": None,
            "role_given": None,
            "mod_roles": [],
            "command_permissions": {
                "giverole": {}, "removerole": {}, "addusertochannel": {}, "removeuserfromchannel": {}
            },
            "timeout_action": "remind",
            "timeout_limit": 86400,
            "reminder_interval": 3600,
            "reminder_timeout": 86400,
            "post_reminder_action": "continue_wait",
            "post_reminder_message": "Your verification period has expired. Please contact a moderator.",
            "reminder_message": "Reminder {user}, please submit your full name to verify and gain access to the server.",
            "verification_confirmation_enabled": True,
            "verification_confirmation_message": "Thank you, {user}! You have been verified and granted access to {server}.",
            "verification_confirmation_dm": True,
            "log_channel": None
        }
        await save_guild_config(interaction.guild, default_config)
        await interaction.response.send_message("✅ Server configuration has been reset to default settings.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetupCog(bot))
