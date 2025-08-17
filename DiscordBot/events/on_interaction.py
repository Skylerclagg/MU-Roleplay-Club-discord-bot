import discord
from discord.ext import commands
from utils.logger import send_log # Import the new logger

class InteractionLogger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        # Log only slash command interactions.
        if interaction.type == discord.InteractionType.application_command and interaction.guild:
            options = interaction.data.get("options", [])
            # Use the new logger instead of print
            log_message = f"Command `/{interaction.data['name']}` invoked by **{interaction.user}** (`{interaction.user.id}`) with options: `{options}`"
            await send_log(self.bot, interaction.guild, log_message)

async def setup(bot: commands.Bot):
    await bot.add_cog(InteractionLogger(bot))
