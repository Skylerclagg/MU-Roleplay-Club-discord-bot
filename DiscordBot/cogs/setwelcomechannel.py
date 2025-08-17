import discord
from discord import app_commands
from discord.ext import commands
from utils.guild_config import get_guild_config, save_guild_config
from utils.permissions import mod_check

class SetWelcomeChannel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setwelcomechannel", description="Set channel for welcome messages.")
    @app_commands.check(mod_check)
    async def setwelcomechannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        config = await get_guild_config(interaction.guild)
        config["welcome_channel"] = channel.id
        await save_guild_config(interaction.guild, config)
        await interaction.response.send_message(f"Welcome channel set to: {channel.mention}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetWelcomeChannel(bot))
