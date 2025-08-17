import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config, save_guild_config
from utils.permissions import mod_check

class SetLogChannel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setlogchannel", description="Set the channel for log output.")
    @app_commands.check(mod_check)
    async def setlogchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild_id = interaction.guild.id
        try:
            # Save the log channel ID in the guild configuration
            config = await get_guild_config(interaction.guild)
            config["log_channel"] = channel.id
            await save_guild_config(interaction.guild, config)
            await interaction.response.send_message(f"✅ Log channel set to {channel.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error setting log channel: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetLogChannel(bot))
