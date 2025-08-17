import discord
from discord import app_commands
from discord.ext import commands
from utils.permissions import mod_check

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Display help info for all commands.")
    @app_commands.check(mod_check)
    async def help(self, interaction: discord.Interaction, command_name: str = None):
            help_message = (
                "**Welcome Bot Help**\n\n"
                "**/setwelcomemessage [message]**: Sets the welcome message (use `{user}` for mention).\n\n"
                "**/setdm [true/false]**: Enables or disables DM verification.\n\n"
                "**/dmmessage [message]**: Sets the DM welcome message (use `{user}` for mention).\n\n"
                "**/setwelcomechannel [channel]**: Sets the welcome channel.\n\n"
                "**/setrolegiven [role]**: Sets the role to assign to new users.\n\n"
                "**/addmodrole [role]**: Adds a mod role.\n\n"
                "**/removemodrole [role]**: Removes a mod role.\n\n"
                "**/listmodroles**: Lists mod roles.\n\n"
                "**/settimeoutaction [action]**: Sets timeout action (kick, restrict, or remind).\n\n"
                "**/settimeoutlimit [time]**: Sets overall verification timeout (e.g., 1d, 1h, 1m, 30s).\n\n"
                "**/setreminderinterval [time]**: Sets the reminder interval (e.g., 1d, 1h, 1m, 30s).\n\n"
                "**/setremindermessage [message]**: Sets the reminder message (use `{user}` for mention).\n\n"
                "**/setremindertimeout [time]**: Sets the overall reminder timeout (in days, e.g., 1d, 2d).\n\n"
                "**/setpostreminderaction [send_dm/continue_wait/kick]**: Sets what happens when overall reminder timeout is reached.\n\n"
                "**/setpostremindermessage [message]**: Sets the custom message for the post-reminder phase.\n\n"
                "**/perms [allow/deny] [user] [command] [value]**: Manages permissions for role/channel commands.\n\n"
                "**/giverole [role] [user]**: Assigns a role (permission controlled).\n\n"
                "**/removerole [role] [user]**: Removes a role (permission controlled).\n\n"
                "**/addusertochannel [channel] [user]**: Adds a user to a channel (permission controlled).\n\n"
                "**/removeuserfromchannel [channel] [user]**: Removes a user from a channel (permission controlled).\n\n"
                "**/manualverify [user] [full_name]**: Manually verify a member.\n\n"
                "**/verifyall [exclude_roles]**: Starts verification for all members without the verified role.\n\n"
                "**/configwelcomechannel [negativerole] [positiverole] [welcomechannel] [excluderoles] [excludecategories]**: Configures welcome channel permissions.\n\n"
                "**/configstatus**: Shows current server configuration.\n\n"
                "**/setlogchannel [channel]**: Sets the channel for log output.\n\n"
                "**/ping**: Checks the bot's latency.\n\n"
            )
            await interaction.response.send_message(help_message, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
