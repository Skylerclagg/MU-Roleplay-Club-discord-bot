import discord
from discord.ui import View, Button, Select, button
from typing import List

# Import config functions
from utils.guild_config import get_guild_config, save_guild_config, format_time, parse_time_limit

# A dictionary to map our internal config keys to user-friendly names
CONFIG_FRIENDLY_NAMES = {
    "welcome_message": "Welcome Message",
    "dm_welcome_message": "DM Welcome Message",
    "reminder_message": "Reminder Message",
    "post_reminder_message": "Post-Timeout Message",
    "verification_confirmation_message": "Confirmation Message",
    "welcome_channel": "Welcome Channel",
    "log_channel": "Log Channel",
    "role_given": "Verified Role",
    "dm_enabled": "DM Verification",
    "reminders_enabled": "Verification Reminders",
    "verification_confirmation_enabled": "Confirmation Messages",
    "timeout_limit": "Verification Timeout Limit",
    "reminder_interval": "Reminder Interval",
    "reminder_timeout": "Overall Reminder Timeout",
    "timeout_action": "Action on Timeout",
    "post_reminder_action": "Action After Overall Timeout",
    "verification_confirmation_dm": "Send Confirmation via DM"
}

class MainSetupView(View):
    """The main view for the /setup command, with category buttons."""
    def __init__(self, original_interaction: discord.Interaction):
        super().__init__(timeout=180)
        self.original_interaction = original_interaction

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try:
            await self.original_interaction.edit_original_response(view=self)
        except discord.NotFound:
            pass # Interaction already gone

    @button(label="General", style=discord.ButtonStyle.secondary, emoji="⚙️")
    async def general_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=await self.get_general_embed(interaction.guild), view=GeneralSettingsView(self.original_interaction))

    @button(label="Verification", style=discord.ButtonStyle.secondary, emoji="✅")
    async def verification_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=await self.get_verification_embed(interaction.guild), view=VerificationSettingsView(self.original_interaction))

    @button(label="Roles", style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def roles_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=await self.get_roles_embed(interaction.guild), view=RoleSettingsView(self.original_interaction))

    @button(label="Close Panel", style=discord.ButtonStyle.danger, emoji="✖️", row=1)
    async def close_button(self, interaction: discord.Interaction, button: Button):
        await interaction.message.delete()

    # --- Embed Generation ---
    async def get_general_embed(self, guild: discord.Guild) -> discord.Embed:
        config = await get_guild_config(guild)
        embed = discord.Embed(title="⚙️ General Settings", description="Configure channels and messages for the bot.", color=discord.Color.blue())
        
        # Channels
        welcome_channel = guild.get_channel(config.get("welcome_channel"))
        log_channel = guild.get_channel(config.get("log_channel"))
        embed.add_field(name="Channels", value=f"**Welcome:** {welcome_channel.mention if welcome_channel else 'Not Set'}\n**Logs:** {log_channel.mention if log_channel else 'Not Set'}", inline=False)
        
        # Messages
        embed.add_field(name="Messages", value=(
            f"Use the dropdowns below to set the bot's messages.\n"
            f"**Placeholders:** Use `{'{user}'}` for the member's mention and `{'{server}'}` for the server name."
        ), inline=False)
        return embed

    async def get_verification_embed(self, guild: discord.Guild) -> discord.Embed:
        config = await get_guild_config(guild)
        embed = discord.Embed(title="✅ Verification Settings", description="Configure the member verification process.", color=discord.Color.green())
        
        dm_status = "Enabled" if config.get("dm_enabled") else "Disabled"
        reminders_status = "Enabled" if config.get("reminders_enabled") else "Disabled"
        confirm_status = "Enabled" if config.get("verification_confirmation_enabled") else "Disabled"
        confirm_dm_status = "via DM" if config.get("verification_confirmation_dm") else "in Welcome Channel"
        
        embed.add_field(name="Toggles", value=f"**DM Verification:** {dm_status}\n**Reminders:** {reminders_status}\n**Confirmations:** {confirm_status} ({confirm_dm_status})", inline=False)
        
        embed.add_field(name="Durations", value=(
            f"**Timeout Limit:** {format_time(config.get('timeout_limit', 86400))}\n"
            f"**Reminder Interval:** {format_time(config.get('reminder_interval', 3600))}\n"
            f"**Overall Timeout:** {format_time(config.get('reminder_timeout', 86400))}"
        ), inline=False)
        
        embed.add_field(name="Actions", value=(
            f"**Action on Timeout:** `{config.get('timeout_action', 'remind')}`\n"
            f"**Action after Overall Timeout:** `{config.get('post_reminder_action', 'continue_wait')}`"
        ), inline=False)
        return embed

    async def get_roles_embed(self, guild: discord.Guild) -> discord.Embed:
        config = await get_guild_config(guild)
        embed = discord.Embed(title="🛡️ Role Settings", description="Manage verified and moderator roles.", color=discord.Color.gold())

        verified_role = guild.get_role(config.get("role_given"))
        embed.add_field(name="Verified Role", value=f"{verified_role.mention if verified_role else 'Not Set'}", inline=False)
        
        mod_roles = [guild.get_role(rid) for rid in config.get("mod_roles", [])]
        mod_role_mentions = [r.mention for r in mod_roles if r]
        embed.add_field(name="Moderator Roles", value="\n".join(mod_role_mentions) if mod_role_mentions else "None", inline=False)
        return embed

# --- Child Views ---

class GeneralSettingsView(MainSetupView):
    def __init__(self, original_interaction: discord.Interaction):
        super().__init__(original_interaction)
        # Add components for this view
        self.add_item(self.MessageSelect())
        self.add_item(self.ChannelSelect())
        self.add_item(self.BackButton())

    class BackButton(Button):
        def __init__(self):
            super().__init__(label="Back", style=discord.ButtonStyle.grey, emoji="↩️", row=2)
        async def callback(self, interaction: discord.Interaction):
            # Go back to the main view
            view = MainSetupView(interaction)
            embed = discord.Embed(title="Bot Setup Panel", description="Select a category to configure.", color=discord.Color.purple())
            await interaction.response.edit_message(embed=embed, view=view)

    class MessageSelect(Select):
        def __init__(self):
            options = [discord.SelectOption(label=name, value=key) for key, name in CONFIG_FRIENDLY_NAMES.items() if "message" in key]
            super().__init__(placeholder="Configure a bot message...", options=options, row=0)
        
        async def callback(self, interaction: discord.Interaction):
            # Logic for modal to set message would go here
            await interaction.response.send_message("This is a placeholder for a modal to set the message.", ephemeral=True)

    class ChannelSelect(Select):
        def __init__(self):
            options = [discord.SelectOption(label=name, value=key) for key, name in CONFIG_FRIENDLY_NAMES.items() if "channel" in key]
            super().__init__(placeholder="Configure a channel...", options=options, channel_types=[discord.ChannelType.text], row=1)
        
        async def callback(self, interaction: discord.Interaction):
            key = self.values[0]
            channel = interaction.guild.get_channel(int(self.values[0])) # This is how you get the channel from the select
            
            config = await get_guild_config(interaction.guild)
            config[key] = channel.id
            await save_guild_config(interaction.guild, config)
            
            await interaction.response.send_message(f"✅ **{CONFIG_FRIENDLY_NAMES[key]}** set to {channel.mention}", ephemeral=True)
            # Refresh the embed
            await interaction.message.edit(embed=await self.view.get_general_embed(interaction.guild))


class VerificationSettingsView(MainSetupView):
    def __init__(self, original_interaction: discord.Interaction):
        super().__init__(original_interaction)
        self.add_item(self.ToggleSelect())
        self.add_item(self.ActionSelect())
        self.add_item(GeneralSettingsView.BackButton())
    
    class ToggleSelect(Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="Enable DM Verification", value="dm_enabled"),
                discord.SelectOption(label="Disable DM Verification", value="dm_enabled_off"),
                discord.SelectOption(label="Enable Reminders", value="reminders_enabled"),
                discord.SelectOption(label="Disable Reminders", value="reminders_enabled_off"),
            ]
            super().__init__(placeholder="Toggle features...", options=options, row=0)

        async def callback(self, interaction: discord.Interaction):
            value = self.values[0]
            key = value.replace("_off", "")
            enabled = not value.endswith("_off")

            config = await get_guild_config(interaction.guild)
            config[key] = enabled
            await save_guild_config(interaction.guild, config)
            
            status = "enabled" if enabled else "disabled"
            await interaction.response.send_message(f"✅ **{CONFIG_FRIENDLY_NAMES[key]}** has been {status}.", ephemeral=True)
            await interaction.message.edit(embed=await self.view.get_verification_embed(interaction.guild))

    class ActionSelect(Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="On Timeout: Kick", value="timeout_action_kick"),
                discord.SelectOption(label="On Timeout: Remind", value="timeout_action_remind"),
                discord.SelectOption(label="After Timeout: Kick", value="post_reminder_action_kick"),
                discord.SelectOption(label="After Timeout: Send DM", value="post_reminder_action_send_dm"),
            ]
            super().__init__(placeholder="Configure timeout actions...", options=options, row=1)

        async def callback(self, interaction: discord.Interaction):
            parts = self.values[0].split('_')
            key = f"{parts[0]}_{parts[1]}"
            action = parts[2]
            
            config = await get_guild_config(interaction.guild)
            config[key] = action
            await save_guild_config(interaction.guild, config)

            await interaction.response.send_message(f"✅ **{CONFIG_FRIENDLY_NAMES[key]}** set to `{action}`.", ephemeral=True)
            await interaction.message.edit(embed=await self.view.get_verification_embed(interaction.guild))


class RoleSettingsView(MainSetupView):
    def __init__(self, original_interaction: discord.Interaction):
        super().__init__(original_interaction)
        self.add_item(self.VerifiedRoleSelect())
        self.add_item(self.ModRoleSelect(add=True))
        self.add_item(self.ModRoleSelect(add=False))
        self.add_item(GeneralSettingsView.BackButton())

    class VerifiedRoleSelect(Select):
        def __init__(self):
            super().__init__(placeholder="Set the verified role...", role_select=True, row=0)

        async def callback(self, interaction: discord.Interaction):
            role_id = int(self.values[0])
            role = interaction.guild.get_role(role_id)
            
            config = await get_guild_config(interaction.guild)
            config["role_given"] = role_id
            await save_guild_config(interaction.guild, config)

            await interaction.response.send_message(f"✅ **Verified Role** set to {role.mention}", ephemeral=True)
            await interaction.message.edit(embed=await self.view.get_roles_embed(interaction.guild))

    class ModRoleSelect(Select):
        def __init__(self, add: bool):
            self.add = add
            super().__init__(
                placeholder=f"{( 'Add' if add else 'Remove')} a mod role...", 
                role_select=True, 
                row=(1 if add else 2)
            )

        async def callback(self, interaction: discord.Interaction):
            role_id = int(self.values[0])
            role = interaction.guild.get_role(role_id)

            config = await get_guild_config(interaction.guild)
            mod_roles = config.get("mod_roles", [])

            if self.add:
                if role_id not in mod_roles:
                    mod_roles.append(role_id)
                    msg = f"✅ {role.mention} is now a mod role."
                else:
                    msg = f"⚠️ {role.mention} is already a mod role."
            else: # Remove
                if role_id in mod_roles:
                    mod_roles.remove(role_id)
                    msg = f"✅ {role.mention} is no longer a mod role."
                else:
                    msg = f"⚠️ {role.mention} was not a mod role."
            
            config["mod_roles"] = mod_roles
            await save_guild_config(interaction.guild, config)
            
            await interaction.response.send_message(msg, ephemeral=True)
            await interaction.message.edit(embed=await self.view.get_roles_embed(interaction.guild))
