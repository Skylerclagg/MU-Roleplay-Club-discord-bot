import discord
from discord import app_commands
from discord.ext import commands
from utils.permissions import mod_check

class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check the bot's latency.")
    async def ping(self, interaction: discord.Interaction):
        latency = self.bot.latency * 1000  # Convert to milliseconds
        await interaction.response.send_message(f"Pong! Latency: {latency:.2f} ms", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))
