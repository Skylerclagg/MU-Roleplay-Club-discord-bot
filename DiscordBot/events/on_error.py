import discord
from discord import app_commands
from discord.ext import commands

class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            try:
                await interaction.response.send_message(
                    "You are not authorized to use this command.", 
                    ephemeral=True
                )
            except discord.InteractionResponded:
                await interaction.followup.send(
                    "You are not authorized to use this command.",
                    ephemeral=True
                )
            except Exception as e:
                print(f"Failed to send auth error message: {e}")
        else:
            # You can add more error handling here for other types of errors
            print(f"An unhandled command error occurred: {error}")


async def setup(bot: commands.Bot):
    await bot.add_cog(ErrorHandler(bot))
