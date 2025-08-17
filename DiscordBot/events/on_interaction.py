import discord
from discord.ext import commands

class InteractionLogger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        # Log only slash command interactions.
        if interaction.type == discord.InteractionType.application_command:
            options = interaction.data.get("options", [])
            print(f"Interaction: Command `{interaction.data['name']}` invoked by {interaction.user} with options: {options}")

async def setup(bot: commands.Bot):
    await bot.add_cog(InteractionLogger(bot))
