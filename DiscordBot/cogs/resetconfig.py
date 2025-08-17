import discord
from discord.ext import commands
from discord import app_commands
from utils.guild_config import get_guild_config, save_guild_config
from utils.permissions import mod_check

class ResetConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="resetconfig", description="Reset the server configuration to its default settings.")
    @app_commands.check(mod_check)
    async def resetconfig(self, interaction: discord.Interaction):
        # Get the default configuration structure
        default_config = {
            "welcome_message": "Welcome {user}! Please reply with your full name to verify.",
            "dm_enabled": False,
            "dm_welcome_message": "Hello {user}, welcome! Please reply with your full name to verify.",
            "welcome_channel": None,
            "role_given": None,
            "mod_roles": [],
            "command_permissions": {
                "giverole": {},
                "removerole": {},
                "addusertochannel": {},
                "removeuserfromchannel": {}
            },
            "timeout_action": "remind",
            "timeout_limit": 86400,
            "reminder_interval": 3600,
            "reminder_message": "Reminder {user}, please submit your full name to verify and gain access to the server."
        }

        # Save the default configuration back to the server
        await save_guild_config(interaction.guild, default_config)

        await interaction.response.send_message(
            "Server configuration has been reset to default settings.", ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(ResetConfig(bot))
